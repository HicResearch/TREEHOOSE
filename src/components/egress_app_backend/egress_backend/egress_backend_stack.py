# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
from os import path

import aws_cdk.aws_amplify as amplify
import aws_cdk.aws_appsync as appsync
import aws_cdk.aws_cognito as cognito
import aws_cdk.aws_dynamodb as ddb
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_efs as efs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda as lmb
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_notifications as s3n
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as subscriptions
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as sfn_tasks
from aws_cdk import core as cdk
from aws_cdk.core import Duration, Tags
from cdk_nag import NagSuppressions
from components.email_configuration_set.email_configuration_set_cr import (
    EmailConfigurationSetCustomResource,
)
from components.email_configuration_set_event_dest.email_configuration_set_event_dest_cr import (
    EmailConfigurationSetEventDestinationCustomResource,
)
from components.email_identity.email_identity_verification_cr import (
    EmailIdentityVerificationCustomResource,
)


class EgressBackendStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, env_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import existing SNS topic
        swb_egress_topic = sns.Topic.from_topic_arn(
            self,
            "swb-egress-topic",
            self.node.try_get_context(env_id).get("swb_egress_notification_topic"),
        )

        # Import existing SWB Egress Store Bucket
        swb_egress_store_bucket = s3.Bucket.from_bucket_arn(
            self,
            "swb-egress-store-bucket",
            self.node.try_get_context(env_id).get("swb_egress_store_arn"),
        )

        # Import existing SWB Egress Notification Bucket
        swb_egress_notification_bucket = s3.Bucket.from_bucket_arn(
            self,
            "swb_egress_notification_bucket_arn",
            self.node.try_get_context(env_id).get("swb_egress_notification_bucket_arn"),
        )

        # Import existing SWB Egress NotificationBucket KMS key
        swb_egress_notification_bucket_kms_key = kms.Key.from_key_arn(
            self,
            "swb-egress-notification-bucket-kms-key",
            self.node.try_get_context(env_id).get(
                "swb_egress_notification_bucket_kms_arn"
            ),
        )

        # Import existing SWB Egress Store DynamoDB Table
        swb_egress_store_db_table = ddb.Table.from_table_arn(
            self,
            "swb-egress-store-db-table",
            self.node.try_get_context(env_id).get("swb_egress_store_db_table"),
        )

        # Import existing DataLake target Bucket
        datalake_bucket = s3.Bucket.from_bucket_arn(
            self,
            "datalake-target-bucket",
            self.node.try_get_context(env_id).get("datalake_target_bucket_arn"),
        )

        # Import existing DataLake target Bucket KMS key
        datalake_bucket_kms_key = kms.Key.from_key_arn(
            self,
            "datalake-target-bucket-kms-key",
            self.node.try_get_context(env_id).get("datalake_target_bucket_kms_arn"),
        )

        # Variable for the project name
        tre_project = self.node.try_get_context(env_id)["resource_tags"]["ProjectName"]

        # Variable for the EFS mount path
        efs_mount_path = self.node.try_get_context(env_id).get("efs_mount_path")

        # Load base config
        base_config = self.node.try_get_context("base")

        # Define Lambda Powertools layer
        powertools_layer = lmb.LayerVersion.from_layer_version_arn(
            self,
            "LambdaPowertoolsLayer",
            layer_version_arn=self.node.try_get_context(env_id).get(
                "powertools_lambda_layer_arn"
            ),
        )

        # Variable for TRE admin email address
        tre_admin_email_address = self.node.try_get_context(env_id).get(
            "tre_admin_email_address"
        )

        # The code that defines your stack goes here
        this_dir = path.dirname(__file__)

        # SES Configuration Set components
        ses_config_set_name = f"{base_config['ses_configuration_set_name']}{env_id}"

        ses_configuration_set = EmailConfigurationSetCustomResource(
            self,
            "EmailConfigurationSetCustomResource",
            account_id=self.account,
            region=self.region,
            env_id=env_id,
            configuration_set_name=ses_config_set_name,
        )
        ses_monitoring_sns_topic = sns.Topic(self, "SES-Monitoring-Notifications")

        sns_configuration_set_destination = (
            EmailConfigurationSetEventDestinationCustomResource(
                self,
                "EmailConfigurationSetEventDestinationCustomResource",
                account_id=self.account,
                region=self.region,
                env_id=env_id,
                configuration_set_name=ses_config_set_name,
                destination_topic_arn=ses_monitoring_sns_topic.topic_arn,
            )
        )

        # Custom resource to handle email identity verification
        ses_sender_email_verification = EmailIdentityVerificationCustomResource(
            self,
            "SESEmailIdentityVerification",
            account_id=self.account,
            region=self.region,
            env_id=env_id,
            ses_sender_email=tre_admin_email_address,
            configuration_set_name=ses_config_set_name,
        )

        # Ensure configuration set is created before email verification
        ses_sender_email_verification.node.add_dependency(ses_configuration_set)

        # Ensure configuration set is created before configuration set destination
        sns_configuration_set_destination.node.add_dependency(ses_configuration_set)

        # Create a custom VPC which will be needed for the EFS mount point.
        # This is required by the copy to datalake lambda to gain access to elastic storage to support the zipping process
        vpc = ec2.Vpc(
            self,
            "TRE-VPC",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24, name="efs", subnet_type=ec2.SubnetType.ISOLATED
                )
            ],
        )

        # Attach a flow log to the vpc
        vpc_log_group = logs.LogGroup(self, "VpcFlowLogGroup")
        vpc_flow_log_role = iam.Role(
            self,
            "VpcFlowLogRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
        )
        ec2.FlowLog(
            self,
            "VpcFlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                vpc_log_group, vpc_flow_log_role
            ),
        )

        # Create EFS file system
        file_system = efs.FileSystem(
            self, "FileSystem", vpc=vpc, removal_policy=cdk.RemovalPolicy.DESTROY
        )

        file_access_point = file_system.add_access_point(
            "AccessPoint",
            create_acl=efs.Acl(owner_gid="1001", owner_uid="1001", permissions="750"),
            path="/export/lambda",
            posix_user=efs.PosixUser(gid="1001", uid="1001"),
        )

        # Create S3 VPC Gateway Endpoint to allow Lambda function comms to S3
        ec2.GatewayVpcEndpoint(
            self, "S3VpcEndpoint", vpc=vpc, service=ec2.GatewayVpcEndpointAwsService.S3
        )

        # Create KMS keys for resources
        s3_kms_key = kms.Key(
            self, "Egress-S3-Key", alias="alias/Egress-S3-Key", enable_key_rotation=True
        )

        dynamodb_kms_key = kms.Key(
            self,
            "Egress-DynamoDB-Key",
            alias="alias/Egress-DynamoDB-Key",
            enable_key_rotation=True,
        )

        sns_kms_key = kms.Key(
            self,
            "Egress-Sns-Key",
            alias="alias/Egress-Sns-Key",
            enable_key_rotation=True,
        )

        # Define DynamoDB table to hold egress requests
        egress_requests_table = ddb.Table(
            self,
            "Egress-Requests-Table",
            partition_key=ddb.Attribute(
                name="egress_request_id", type=ddb.AttributeType.STRING
            ),
            encryption=ddb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=dynamodb_kms_key,
            billing_mode=ddb.BillingMode.PROVISIONED,
            point_in_time_recovery=True,
        )

        # Define SNS topics for notifying reviewers
        ig_role_topic = sns.Topic(
            self,
            "Information-Governance-Egress-Topic",
            display_name=f"{tre_project} Information Governance Notifications",
            topic_name="Information-Governance-Notifications",
            master_key=sns_kms_key,
        )

        rit_role_topic = sns.Topic(
            self,
            "ResearchIT-Egress-Topic",
            display_name=f"{tre_project} Research IT Notifications",
            topic_name="ResearchIT-Notifications",
            master_key=sns_kms_key,
        )

        # Define server access logs bucket to monitor staging bucket
        access_logs_bucket = s3.Bucket(
            self,
            "AccessLogsBucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=s3_kms_key,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # Add Egress Staging Bucket
        egress_staging_bucket = s3.Bucket(
            self,
            "Egress-Staging-Bucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=s3_kms_key,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            server_access_logs_bucket=access_logs_bucket,
            server_access_logs_prefix="egress_staging_logs",
        )

        # Add dataset tags to bucket
        for tag_key, tag_value in self.node.try_get_context(env_id)["dataset"].items():
            Tags.of(egress_staging_bucket).add(tag_key, tag_value)

        # Add Amplify App
        amplify_branch_name = "main"
        amplify_app = amplify.App(self, "EgressFrontendApp")
        amplify_app.add_branch(amplify_branch_name)
        egress_app_url = (
            f"https://{amplify_branch_name}.{amplify_app.app_id}.amplifyapp.com"
        )

        # Add Egress Web App Bucket
        egress_webapp_bucket = s3.Bucket(
            self,
            "Egress-WebApp-Bucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            server_access_logs_bucket=access_logs_bucket,
            server_access_logs_prefix="egress_webapp_logs",
        )

        egress_webapp_redeploy_lambda_role = iam.Role(
            self,
            "egress-webapp-redeploy-lambda-role",
            description="Role used by egress_webapp_redeploy_function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        egress_webapp_redeploy_lambda_policy = iam.ManagedPolicy(
            self,
            "egress-webapp-redeploy-lambda-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:GetObject",
                        "s3:GetObjectAcl",
                        "s3:PutObjectAcl",
                        "s3:ListBucket",
                    ],
                    resources=[
                        f"{egress_webapp_bucket.bucket_arn}/*",
                        f"{egress_webapp_bucket.bucket_arn}",
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["amplify:StartDeployment"],
                    resources=[
                       f"arn:aws:amplify:{self.region}:{self.account}:apps/{amplify_app.app_id}/branches/{amplify_branch_name}/deployments/start"
                    ],
                ),
            ],
        )

        egress_webapp_redeploy_lambda_role.add_managed_policy(
            egress_webapp_redeploy_lambda_policy
        )

        egress_webapp_redeploy_function = lmb.Function(
            self,
            "egress-webapp-redeploy-function",
            description="Lambda function which redeploys packaged code to Amplify to update the egress web app",
            function_name="egress_webapp_redeploy",
            handler="egress_webapp_redeploy.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/egress_webapp_redeploy")
            ),
            layers=[powertools_layer],
            role=egress_webapp_redeploy_lambda_role,
            timeout=Duration.seconds(60),
            environment={
                "EGRESS_WEBAPP_BUCKET_NAME": egress_webapp_bucket.bucket_name,
                "EGRESS_WEBAPP_ID": amplify_app.app_id,
                "EGRESS_WEBAPP_BRANCH": amplify_branch_name,
                "REGION": self.region,
            },
        )

        egress_webapp_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(egress_webapp_redeploy_function),
        )

        # Define Egress Workflow Step Function Tasks
        add_request_to_db_task = sfn_tasks.DynamoPutItem(
            self,
            "Save Request To DynamoDB",
            item={
                "egress_request_id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_request_id")
                ),
                "swb_egress_store_id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_store_id")
                ),
                "project_id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.project_id")
                ),
                "egress_status": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.status")
                ),
                "workspace_id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.workspace_id")
                ),
                "egress_store_name": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_store_name")
                ),
                "s3_egress_store_bucket": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.s3_bucketname")
                ),
                "s3_egress_store_bucket_path": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.s3_bucketpath")
                ),
                "s3_egress_store_object_list_location": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_store_object_list_location")
                ),
                "requested_by": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.created_by_email")
                ),
                "requested_dt": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.created_at")
                ),
                "updated_by": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.updated_by_email")
                ),
                "updated_dt": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.updated_at")
                ),
                "s3_swb_object_metadata_version": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.ver")
                ),
            },
            table=egress_requests_table,
            # Set to None/Null so that original input gets passed on to the next task since we do not
            # need anything from the DynamoDB API response
            result_path=sfn.JsonPath.DISCARD,
        )

        # Define Egress Workflow Step Function task to update DB
        ig_update_request_in_db_task = sfn_tasks.DynamoUpdateItem(
            self,
            "Save Information Governance Decision",
            key={
                "egress_request_id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_request_id")
                )
            },
            table=egress_requests_table,
            update_expression="SET ig_reviewer_1_reason = :reason, \
                ig_reviewer_1_decision = :decision, \
                ig_reviewer_1_email = :email, \
                ig_reviewer_1_dt = :review_date, \
                egress_status = :req_status",
            expression_attribute_values={
                ":reason": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at(
                        "$.information_governance.result.ig_reviewer_1_reason"
                    )
                ),
                ":decision": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at(
                        "$.information_governance.result.ig_reviewer_1_decision"
                    )
                ),
                ":email": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at(
                        "$.information_governance.result.ig_reviewer_1_email"
                    )
                ),
                ":review_date": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at(
                        "$.information_governance.result.ig_reviewer_1_dt"
                    )
                ),
                ":req_status": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at(
                        "$.information_governance.result.egress_status"
                    )
                ),
            },
            result_path=sfn.JsonPath.DISCARD,
        )

        rit_update_request_in_db_task = sfn_tasks.DynamoUpdateItem(
            self,
            "Save Research IT Decision",
            key={
                "egress_request_id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_request_id")
                )
            },
            table=egress_requests_table,
            update_expression="SET rit_reviewer_2_reason = :reason, \
                rit_reviewer_2_decision = :decision, \
                rit_reviewer_2_email = :email, \
                rit_reviewer_2_dt = :review_date, \
                egress_status = :req_status",
            expression_attribute_values={
                ":reason": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.research_it.result.rit_reviewer_2_reason")
                ),
                ":decision": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at(
                        "$.research_it.result.rit_reviewer_2_decision"
                    )
                ),
                ":email": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.research_it.result.rit_reviewer_2_email")
                ),
                ":review_date": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.research_it.result.rit_reviewer_2_dt")
                ),
                ":req_status": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.research_it.result.egress_status")
                ),
            },
            result_path=sfn.JsonPath.DISCARD,
        )

        # Define Egress Workflow Step Function task to notify egress store DB processing of request
        process_request_in_egress_store_db_task = sfn_tasks.DynamoUpdateItem(
            self,
            "Update Request in Egress Store DynamoDB (processing)",
            key={
                "id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_store_id")
                )
            },
            table=swb_egress_store_db_table,
            update_expression="SET #s = :req_status",
            expression_attribute_values={
                ":req_status": sfn_tasks.DynamoAttributeValue.from_string("PROCESSING")
            },
            expression_attribute_names={"#s": "status"},
            result_path=sfn.JsonPath.DISCARD,
        )

        # Define Egress Workflow Step Function task to update egress store DB for Research IT
        update_request_in_egress_store_db_rit_task = sfn_tasks.DynamoUpdateItem(
            self,
            "Update Request in Egress Store DynamoDB (status) - RIT",
            key={
                "id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_store_id")
                )
            },
            table=swb_egress_store_db_table,
            update_expression="SET #s = :req_status",
            expression_attribute_values={
                ":req_status": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.research_it.result.swb_status")
                )
            },
            expression_attribute_names={"#s": "status"},
            result_path=sfn.JsonPath.DISCARD,
        )

        # Define Egress Workflow Step Function task to update egress store DB for IG Lead
        update_request_in_egress_store_db_iglead_task = sfn_tasks.DynamoUpdateItem(
            self,
            "Update Request in Egress Store DynamoDB (status) - IGLead",
            key={
                "id": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.egress_store_id")
                )
            },
            table=swb_egress_store_db_table,
            update_expression="SET #s = :req_status",
            expression_attribute_values={
                ":req_status": sfn_tasks.DynamoAttributeValue.from_string(
                    sfn.JsonPath.string_at("$.information_governance.result.swb_status")
                )
            },
            expression_attribute_names={"#s": "status"},
            result_path=sfn.JsonPath.DISCARD,
        )

        # Define execution & custom policy
        lambda_exec_policy = iam.ManagedPolicy.from_managed_policy_arn(
            self,
            id="lambda-exec-policy-00",
            managed_policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        )

        copy_staging_lambda_role = iam.Role(
            self,
            "copy-egress-candidates-to-staging-role",
            description="Role used by opy_egress_candidates_to_staging_function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        copy_staging_lambda_policy = iam.ManagedPolicy(
            self,
            "copy-egress-candidates-to-staging-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["s3:PutObject*", "s3:Abort*"],
                    resources=[f"{egress_staging_bucket.bucket_arn}/*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:Decrypt",
                    ],
                    resources=[s3_kms_key.key_arn],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["s3:GetObject*", "s3:GetBucket*", "s3:List*"],
                    resources=[
                        swb_egress_store_bucket.bucket_arn,
                        f"{swb_egress_store_bucket.bucket_arn}/*",
                        swb_egress_notification_bucket.bucket_arn,
                        f"{swb_egress_notification_bucket.bucket_arn}/*",
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["kms:Decrypt"],
                    resources=[swb_egress_notification_bucket_kms_key.key_arn],
                ),
            ],
        )

        copy_staging_lambda_role.add_managed_policy(lambda_exec_policy)
        copy_staging_lambda_role.add_managed_policy(copy_staging_lambda_policy)

        # Lambda function which copies egress candidate files to staging bucket
        copy_egress_candidates_to_staging_function = lmb.Function(
            self,
            "copy-egress-candidates-to-staging-function",
            description="Lambda function which copies candidate egress files to egress staging bucket",
            function_name="copy_egress_candidates_to_staging",
            handler="copy_egress_candidates_to_staging.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/copy_egress_candidates_to_staging")
            ),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            role=copy_staging_lambda_role,
            timeout=Duration.seconds(60),
            environment={
                "EGRESS_STAGING_BUCKET": egress_staging_bucket.bucket_name,
                "REGION": self.region,
                "NOTIFICATION_BUCKET": swb_egress_notification_bucket.bucket_name,
            },
        )

        # Define egress copy_to_staging Step Function task
        copy_to_staging_task = sfn_tasks.LambdaInvoke(
            self,
            "Copy Objects To Egress Staging",
            lambda_function=copy_egress_candidates_to_staging_function,
            result_selector={
                "staged": sfn.JsonPath.string_at("$.Payload.staged"),
                "file_extensions": sfn.JsonPath.list_at("$.Payload.file_extensions"),
            },
            result_path="$.copy_to_staging_result",
        )

        # Publish notifications to SNS
        notify_ig_reviewer_task = sfn_tasks.SnsPublish(
            self,
            "Notify Information Governance",
            topic=ig_role_topic,
            subject=sfn.JsonPath.string_at(
                "States.Format('{} Egress Request', $.project_id)"
            ),
            message=sfn.TaskInput.from_object(
                {
                    "Egress Request ID": sfn.JsonPath.string_at("$.egress_request_id"),
                    "Researcher Email": sfn.JsonPath.string_at("$.created_by_email"),
                    "Egress Object File Types": sfn.JsonPath.string_at(
                        "$.copy_to_staging_result.file_extensions"
                    ),
                }
            ),
            result_path=sfn.JsonPath.DISCARD,
        )

        notify_rit_reviewer_task = sfn_tasks.SnsPublish(
            self,
            "Notify Research IT",
            topic=rit_role_topic,
            subject=sfn.JsonPath.string_at(
                "States.Format('{} Egress Request', $.project_id)"
            ),
            message=sfn.TaskInput.from_object(
                {
                    "Egress Request ID": sfn.JsonPath.string_at("$.egress_request_id"),
                    "Researcher Email": sfn.JsonPath.string_at("$.created_by_email"),
                    "Information Governance": sfn.JsonPath.string_at(
                        "$.information_governance.result.ig_reviewer_1_email"
                    ),
                    "Egress Object File Types": sfn.JsonPath.string_at(
                        "$.copy_to_staging_result.file_extensions"
                    ),
                }
            ),
            result_path=sfn.JsonPath.DISCARD,
        )

        # Lambda function which writes the task token to DynamoDB so workflow can be resumed later
        update_egress_request_with_task_token_function = lmb.Function(
            self,
            "update-egress-request-with-task-token-function",
            description="Lambda function which updated egress requests in DynamoDB with a Step Function task token",
            function_name="update_egress_request_with_task_token",
            handler="update_egress_request_with_task_token.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/update_egress_request")
            ),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            timeout=Duration.seconds(10),
            environment={
                "TABLE": egress_requests_table.table_name,
                "REGION": self.region,
            },
        )

        # Grant the update lambda permission to access the DynamoDB table
        egress_requests_table.grant_read_write_data(
            update_egress_request_with_task_token_function
        )

        # Task to pause and wait for IG decision
        ig_decision_task = sfn_tasks.LambdaInvoke(
            self,
            "Information Governance Decision",
            lambda_function=update_egress_request_with_task_token_function,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=sfn.TaskInput.from_object(
                {
                    "token": sfn.JsonPath.task_token,
                    "input": sfn.JsonPath.string_at("$.egress_request_id"),
                    "current_reviewer_group": sfn.JsonPath.string_at(
                        "$.reviewer_list[0]"
                    ),
                }
            ),
            result_selector={"result": sfn.JsonPath.string_at("$.request")},
            result_path="$.information_governance",
        )

        # Task to pause and wait for RIT decision
        rit_decision_task = sfn_tasks.LambdaInvoke(
            self,
            "Research IT Decision",
            lambda_function=update_egress_request_with_task_token_function,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=sfn.TaskInput.from_object(
                {
                    "token": sfn.JsonPath.task_token,
                    "input": sfn.JsonPath.string_at("$.egress_request_id"),
                    "current_reviewer_group": sfn.JsonPath.string_at(
                        "$.reviewer_list[1]"
                    ),
                }
            ),
            result_selector={"result": sfn.JsonPath.string_at("$.request")},
            result_path="$.research_it",
        )

        # Choice task to check if request has been approved
        check_ig_approval = sfn.Choice(self, "Information Governance Approved?")
        check_rit_approval = sfn.Choice(self, "Research IT Approved?")

        # Lambda function which tags egress candidate files as rejected in the staging bucket
        handle_egress_rejection_function = lmb.Function(
            self,
            "handle-egress-rejection-function",
            description="Lambda function which tags egress candidate files as rejected in the staging bucket",
            function_name="handle_egress_rejection",
            handler="handle_egress_rejection.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/handle_egress_rejection")
            ),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            timeout=Duration.seconds(10),
            environment={
                "EGRESS_STAGING_BUCKET": egress_staging_bucket.bucket_name,
                "REGION": self.region,
            },
        )

        # Need to add a custom policy as the grant_put method does not add the PutObjectTagging permission
        handle_egress_rejection_function.add_to_role_policy(
            iam.PolicyStatement(
                sid="S3permissions",
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObjectTagging",
                    "s3:GetBucket*",
                    "s3:GetObject*",
                    "s3:DeleteObject*",
                    "s3:List*",
                ],
                resources=[
                    egress_staging_bucket.bucket_arn,
                    f"{egress_staging_bucket.bucket_arn}/*",
                ],
            )
        )
        handle_egress_rejection_function.add_to_role_policy(
            iam.PolicyStatement(
                sid="KMSpermissions",
                effect=iam.Effect.ALLOW,
                actions=[
                    "kms:Decrypt",
                    "kms:Encrypt",
                    "kms:GenerateDataKey*",
                    "kms:ReEncrypt*",
                ],
                resources=[s3_kms_key.key_arn],
            )
        )

        # Define egress copy_to_staging Step Function task
        handle_egress_rejection_rit_task = sfn_tasks.LambdaInvoke(
            self,
            "Delete Rejected Objects From Staging - RIT",
            lambda_function=handle_egress_rejection_function,
            result_selector={
                "rejected_tag_applied": sfn.JsonPath.string_at("$.Payload")
            },
            result_path="$.handle_egress_rejection_result",
        )

        # Define egress copy_to_staging Step Function task
        handle_egress_rejection_iglead_task = sfn_tasks.LambdaInvoke(
            self,
            "Delete Rejected Objects From Staging - IGLead",
            lambda_function=handle_egress_rejection_function,
            result_selector={
                "rejected_tag_applied": sfn.JsonPath.string_at("$.Payload")
            },
            result_path="$.handle_egress_rejection_result",
        )

        # Lambda function which copies approved egress files to datalake bucket
        copy_egress_candidates_to_datalake_function = lmb.Function(
            self,
            "copy-egress-candidates-to-datalake-function",
            description="Lambda function which copies candidate egress files to egress datalake bucket",
            function_name="copy_egress_candidates_to_datalake",
            handler="copy_egress_candidates_to_datalake.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/copy_egress_candidates_to_datalake")
            ),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            timeout=Duration.seconds(180),
            memory_size=1024,
            environment={
                "EGRESS_STAGING_BUCKET": egress_staging_bucket.bucket_name,
                "EGRESS_DATALAKE_BUCKET": datalake_bucket.bucket_name,
                "EGRESS_DATALAKE_BUCKET_KMS_KEY": datalake_bucket_kms_key.key_arn,
                "EFS_MOUNT_PATH": efs_mount_path + "/",  # Need the extra slash
                "REGION": self.region,
            },
            vpc=vpc,
            filesystem=lmb.FileSystem.from_efs_access_point(
                file_access_point, efs_mount_path
            ),
        )

        # Grant copy lambda function permission to write to datalake bucket
        datalake_bucket.grant_put(copy_egress_candidates_to_datalake_function)

        # Grant copy lambda function permission to use KMS key of the staging bucket
        s3_kms_key.grant_decrypt(copy_egress_candidates_to_datalake_function)

        # Grant copy lambda function permission to use KMS key of the datalake bucket
        datalake_bucket_kms_key.grant_encrypt_decrypt(
            copy_egress_candidates_to_datalake_function
        )

        # Grant copy lambda function permission to read/delete from egress staging bucket
        egress_staging_bucket.grant_read(copy_egress_candidates_to_datalake_function)
        egress_staging_bucket.grant_delete(copy_egress_candidates_to_datalake_function)

        # Define egress copy_to_staging Step Function task
        copy_to_datalake_task = sfn_tasks.LambdaInvoke(
            self,
            "Copy Approved Objects To Datalake",
            lambda_function=copy_egress_candidates_to_datalake_function,
            result_selector={
                "transferred_to_datalake": sfn.JsonPath.string_at("$.Payload")
            },
            result_path="$.copy_to_datalake_result",
        )

        # Define pre-token-generation lambda trigger
        pre_token_generation_fn = lmb.Function(
            self,
            "Pre-Token-Generation-Function",
            description="Lambda function which customises the SAML response to handle group mappings",
            function_name="pre_token_generation",
            handler="pre_token_generation.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/pre_token_generation")
            ),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            timeout=Duration.seconds(10),
            environment={
                "REVIEWER_LIST": json.dumps(
                    self.node.try_get_context(env_id).get("egress_reviewer_roles")
                ),
                "REGION": self.region,
            },
        )

        # Define Cognito resources to handle authentication
        egress_user_pool = cognito.UserPool(
            self,
            "EgressUserPool",
            self_sign_up_enabled=False,
            sign_in_case_sensitive=False,
            sign_in_aliases={"email": True},
            auto_verify={"email": True},
            password_policy={
                "min_length": 12,
                "require_lowercase": True,
                "require_uppercase": True,
                "require_digits": True,
                "require_symbols": True,
                "temp_password_validity": cdk.Duration.days(3),
            },
            custom_attributes={
                "groups": cognito.StringAttribute(min_len=0, max_len=2048, mutable=True)
            },
            lambda_triggers={"pre_token_generation": pre_token_generation_fn},
            mfa=cognito.Mfa.OFF,
        )

        # Create required userpool groups
        user_pool_group = self.node.try_get_context(env_id).get("egress_reviewer_roles")
        for group in user_pool_group:
            cognito.CfnUserPoolGroup(
                self,
                f"{group}UserPoolGroup",
                user_pool_id=egress_user_pool.user_pool_id,
                group_name=group,
            )

        # Add user pool app client
        app_client = cognito.CfnUserPoolClient(
            self,
            "Egress-App-Client",
            supported_identity_providers=["COGNITO"],
            client_name="EgressWebApp",
            allowed_o_auth_flows_user_pool_client=True,
            allowed_o_auth_flows=["code"],
            allowed_o_auth_scopes=[
                "email",
                "openid",
                "profile",
                "aws.cognito.signin.user.admin",
            ],
            explicit_auth_flows=["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"],
            prevent_user_existence_errors="ENABLED",
            generate_secret=False,
            refresh_token_validity=1,
            callback_ur_ls=[egress_app_url],
            logout_ur_ls=[egress_app_url],
            user_pool_id=egress_user_pool.user_pool_id,
        )

        # Add Cognito Userpool domain
        cognito_userpool_domain = self.node.try_get_context(env_id).get(
            "cognito_userpool_domain"
        )
        cognito.CfnUserPoolDomain(
            self,
            "CognitoDomain",
            domain=cognito_userpool_domain,
            user_pool_id=egress_user_pool.user_pool_id,
        )

        # Define AppSync API with user pool authorization and defined schema
        appsync_api = appsync.GraphqlApi(
            self,
            "Egress-Api",
            name="Egress-API",
            schema=appsync.Schema.from_asset("egress_backend/graphql/schema.graphql"),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.USER_POOL,
                    user_pool_config=appsync.UserPoolConfig(
                        user_pool=egress_user_pool,
                        app_id_client_regex=app_client.ref,
                        default_action=appsync.UserPoolDefaultAction.ALLOW,
                    ),
                )
            ),
        )

        send_final_decision_email = sfn_tasks.CallAwsService(
            self,
            "Notify Requester",
            service="sesv2",
            action="sendEmail",
            parameters={
                "FromEmailAddress": tre_admin_email_address,
                "Destination": {
                    "ToAddresses": sfn.JsonPath.string_at(
                        "States.Array($.created_by_email)"
                    ),
                    "CcAddresses": sfn.JsonPath.string_at(
                        "States.Array($.information_governance.result.ig_reviewer_1_email)"
                    ),
                },
                "Content": {
                    "Simple": {
                        "Subject": {
                            "Data": sfn.JsonPath.string_at(
                                "States.Format('{} Egress Request Review Completed', $.project_id)"
                            )
                        },
                        "Body": {
                            "Text": {
                                "Data": sfn.JsonPath.string_at(
                                    "States.Format('The review process for egress request {} is complete. \n"
                                    "@ IG Lead, please log in to the egress app ({}) to check the outcome of the review. \n"
                                    "• If the request has been APPROVED please download the data via the egress app "
                                    "and share with the Egress Requester. \n • If the request has been REJECTED please contact "
                                    "the Egress Requester to discuss the reason why. \r\n If you’re unsure what to do please contact "
                                    "the TRE team for guidance: ({}).', $.egress_request_id, $.egress_app_url, $.tre_admin_email_address )"
                                )
                            }
                        },
                    }
                },
                "ConfigurationSetName": ses_config_set_name,
            },
            iam_resources=[
                f"arn:aws:ses:{self.region}:{self.account}:identity/{tre_admin_email_address}"
            ],
            iam_action="ses:sendEmail",
        )

        # Define Egress Workflow Step Function
        workflow_log_group = logs.LogGroup(self, "ApprovalWorkflowLogs")
        data_egress_step_function = sfn.StateMachine(
            self,
            "Data Egress Workflow",
            definition=add_request_to_db_task.next(
                process_request_in_egress_store_db_task
            )
            .next(copy_to_staging_task)
            .next(notify_ig_reviewer_task)
            .next(ig_decision_task)
            .next(ig_update_request_in_db_task)
            .next(
                check_ig_approval.when(
                    sfn.Condition.string_matches(
                        "$.information_governance.result.egress_status", "*APPROVED"
                    ),
                    notify_rit_reviewer_task.next(rit_decision_task)
                    .next(rit_update_request_in_db_task)
                    .next(
                        check_rit_approval.when(
                            sfn.Condition.string_equals(
                                "$.research_it.result.rit_reviewer_2_decision",
                                "APPROVED",
                            ),
                            copy_to_datalake_task.next(
                                update_request_in_egress_store_db_rit_task
                            ),
                        ).when(
                            sfn.Condition.string_equals(
                                "$.research_it.result.rit_reviewer_2_decision",
                                "REJECTED",
                            ),
                            handle_egress_rejection_rit_task.next(
                                update_request_in_egress_store_db_rit_task
                            ),
                        )
                    ),
                )
                .when(
                    sfn.Condition.string_matches(
                        "$.information_governance.result.egress_status", "*REJECTED"
                    ),
                    handle_egress_rejection_iglead_task.next(
                        update_request_in_egress_store_db_iglead_task
                    ),
                )
                .afterwards()
                .next(send_final_decision_email)
            ),
            timeout=Duration.days(21),
            tracing_enabled=True,
            logs=sfn.LogOptions(destination=workflow_log_group, level=sfn.LogLevel.ALL),
        )

        # Grant permission to read from/write to the DynamoDB table to the step function
        egress_requests_table.grant_read_write_data(data_egress_step_function)

        # Grant permission to update Egress store DB table to the step function
        swb_egress_store_db_table.grant_write_data(data_egress_step_function)

        # Grant permission to use the SNS KMS key to the step function
        sns_kms_key.grant_encrypt_decrypt(data_egress_step_function)

        # Grant permission to use SES to the step function
        data_egress_step_function.add_to_role_policy(
            iam.PolicyStatement(
                resources=["*"],
                actions=["ses:SendEmail", "ses:SendTemplatedEmail"],
                sid="EmailSendToPermissions",
            )
        )

        # Lambda function which processes SNS messages
        start_egress_workflow_function = lmb.Function(
            self,
            "start-egress-workflow-function",
            description="Lambda function which triggers the egress workflow step function",
            function_name="start_egress_workflow",
            handler="start_egress_workflow.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(
                path.join(this_dir, "lambda/start_egress_workflow")
            ),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            timeout=Duration.seconds(10),
            environment={
                "STEP_FUNCTION_ARN": data_egress_step_function.state_machine_arn,
                "REVIEWER_LIST": json.dumps(
                    self.node.try_get_context(env_id).get("egress_reviewer_roles")
                ),
                "EGRESS_APP_URL": egress_app_url,
                "EGRESS_APP_ADMIN_EMAIL": tre_admin_email_address,
                "REGION": self.region,
            },
        )

        # Subscribe lambda to SNS topic
        swb_egress_topic.add_subscription(
            subscriptions.LambdaSubscription(start_egress_workflow_function)
        )

        # Grant start execution permission on the step function to start_egress_workflow_function
        data_egress_step_function.grant_start_execution(start_egress_workflow_function)

        # Define lambda API handler
        egress_api_handler = lmb.Function(
            self,
            "Egress-Api-Lambda",
            description="Lambda function which handles API requests",
            function_name="egress_api_handler",
            handler="main.handler",
            runtime=lmb.Runtime.PYTHON_3_8,
            code=lmb.Code.from_asset(path.join(this_dir, "lambda/egress_api")),
            layers=[powertools_layer],
            tracing=lmb.Tracing.ACTIVE,
            timeout=Duration.seconds(10),
            environment={
                "TABLE": egress_requests_table.table_name,
                "STEP_FUNCTION_ARN": data_egress_step_function.state_machine_arn,
                "REGION": self.region,
                "DATALAKE_BUCKET": datalake_bucket.bucket_name,
                "REVIEWER_LIST": json.dumps(
                    self.node.try_get_context(env_id).get("egress_reviewer_roles")
                ),
                "MAX_DOWNLOADS_ALLOWED": self.node.try_get_context(env_id).get(
                    "max_downloads_allowed"
                ),
            },
        )

        # Grant the api lambda permission to access the datalake bucket
        datalake_bucket.grant_read(egress_api_handler)

        # Grant api lambda function permission to use KMS key of the datalake bucket
        datalake_bucket_kms_key.grant_decrypt(egress_api_handler)

        # Grant the api lambda permission to access the DynamoDB table
        egress_requests_table.grant_read_write_data(egress_api_handler)

        # Grant the api lambda permission to send task responses to the step function
        data_egress_step_function.grant_task_response(egress_api_handler)

        lambda_ds = appsync_api.add_lambda_data_source(
            "lambdaDataSource", egress_api_handler
        )

        # Define lambda resolvers according to schema defintion
        lambda_ds.create_resolver(
            type_name="Query",
            field_name="listRequests",
            request_mapping_template=appsync.MappingTemplate.from_string(
                """
            {
                "version": "2017-02-28",
                "operation": "Invoke",
                "payload": {
                    "field":"listRequests",
                    "email":$util.toJson($context.identity.claims.email),
                    "usergroup":$util.toJson($context.identity.claims.get("cognito:groups")),
                    "arguments": $util.toJson($context.arguments)
                }
            }
            """
            ),
            response_mapping_template=appsync.MappingTemplate.from_string(
                """$util.toJson($context.result)"""
            ),
        )

        lambda_ds.create_resolver(
            type_name="Mutation",
            field_name="updateRequest",
            request_mapping_template=appsync.MappingTemplate.from_string(
                """
            {
                "version": "2017-02-28",
                "operation": "Invoke",
                "payload": {
                    "field":"updateRequest",
                    "email":$util.toJson($context.identity.claims.email),
                    "usergroup":$util.toJson($context.identity.claims.get("cognito:groups")),
                    "arguments": $util.toJson($context.arguments)
                }
            }
            """
            ),
            response_mapping_template=appsync.MappingTemplate.from_string(
                """$util.toJson($context.result)"""
            ),
        )

        lambda_ds.create_resolver(
            type_name="Mutation",
            field_name="downloadData",
            request_mapping_template=appsync.MappingTemplate.from_string(
                """
            {
                "version": "2017-02-28",
                "operation": "Invoke",
                "payload": {
                    "field":"downloadData",
                    "email":$util.toJson($context.identity.claims.email),
                    "usergroup":$util.toJson($context.identity.claims.get("cognito:groups")),
                    "arguments": $util.toJson($context.arguments)
                }
            }
            """
            ),
            response_mapping_template=appsync.MappingTemplate.from_string(
                """$util.toJson($context.result)"""
            ),
        )

        # Define CFN NAG Rule Suppressions
        NagSuppressions.add_resource_suppressions(
            ses_sender_email_verification,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Yes wildcard is used but this has been scoped down to the Admin app. \
                        Needed for deployment flexibility and it only applies to logging actions",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{self.stack_name}/LogRetentionaae0aa3c5b4d4f87b02d85b201efdd8a/ServiceRole/DefaultPolicy/Resource",
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Permissions only used for custom resource logging and cannot be customised",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{self.stack_name}/LogRetentionaae0aa3c5b4d4f87b02d85b201efdd8a/ServiceRole/Resource",
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "Permissions only used for custom resource logging and cannot be customised",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{self.stack_name}/AWS679f53fac002430cb0da5b7982bd2287/ServiceRole/Resource",
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "Permissions only used for custom resource logging and cannot be customised",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            start_egress_workflow_function,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            start_egress_workflow_function,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_api_handler,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_api_handler,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            pre_token_generation_fn,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            pre_token_generation_fn,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            copy_egress_candidates_to_datalake_function,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            copy_egress_candidates_to_datalake_function,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            handle_egress_rejection_function,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            handle_egress_rejection_function,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            update_egress_request_with_task_token_function,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            update_egress_request_with_task_token_function,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            copy_staging_lambda_role,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            copy_staging_lambda_policy,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            copy_staging_lambda_role,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "X-Ray tracing permissions need wildcard",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            data_egress_step_function,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Permissions have been scoped to least privilege and wildcard usage validated",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_user_pool,
            [
                {
                    "id": "AwsSolutions-COG3",
                    "reason": "Cognito AdvancedSecurityMode not currently supported in CDK \
                        and has not been identified as a core requirement",
                },
                {
                    "id": "AwsSolutions-COG2",
                    "reason": "Cognito MFA has not been identified as a core requirement",
                },
            ],
        )
        NagSuppressions.add_resource_suppressions(
            appsync_api,
            [
                {
                    "id": "AwsSolutions-ASC3",
                    "reason": "Request level logging only required to be enabled for troubleshooting, \
                        as sensitive data could otherwise be inspected",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            access_logs_bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Server access log bucket does not need its own access logs bucket.",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            ses_configuration_set,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Yes wildcard is used but this has been scoped down to the Admin app. \
                        Needed for deployment flexibility and it only applies to logging actions",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            sns_configuration_set_destination,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Yes wildcard is used but this has been scoped down to the Admin app. \
                        Needed for deployment flexibility and it only applies to logging actions",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            ses_monitoring_sns_topic,
            [
                {
                    "id": "AwsSolutions-SNS2",
                    "reason": "Topic does not contain sensitive or customer data so encryption is unnecessary",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            ses_monitoring_sns_topic,
            [
                {
                    "id": "AwsSolutions-SNS3",
                    "reason": "Topic is not used to publish to HTTP endpoints",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_webapp_redeploy_lambda_policy,
            [{"id": "AwsSolutions-IAM5", "reason": "Wilcard permissions are expected"}],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_webapp_redeploy_lambda_role,
            [{"id": "AwsSolutions-IAM5", "reason": "Wilcard permissions are expected"}],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_webapp_redeploy_lambda_role,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions(
            egress_webapp_redeploy_lambda_role,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{self.stack_name}/BucketNotificationsHandler050a0587b7544547bf325f094a3db834/Role/Resource",
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWS Managed role is used for Lambda Basic Execution Policy",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{self.stack_name}/BucketNotificationsHandler050a0587b7544547bf325f094a3db834/Role/Resource",
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Wilcard permissions are required for S3 notifications",
                }
            ],
            True,
        )
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{self.stack_name}/Egress-Api/lambdaDataSource/ServiceRole/DefaultPolicy/Resource",
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Wildcard permissions are required",
                }
            ],
            True,
        )

        cdk.CfnOutput(
            self,
            "EgressAppURL",
            value=egress_app_url,
            description="The URL for the Egress App.",
        )

        cdk.CfnOutput(
            self,
            "EgressReviewerRole1",
            value=self.node.try_get_context(env_id).get("egress_reviewer_roles")[0],
            description="The Cognito group name for reviewer type 1.",
        )

        cdk.CfnOutput(
            self,
            "EgressReviewerRole2",
            value=self.node.try_get_context(env_id).get("egress_reviewer_roles")[1],
            description="The Cognito group name for reviewer type 2.",
        )

        cdk.CfnOutput(
            self,
            "MaxDownloadsAllowed",
            value=self.node.try_get_context(env_id).get("max_downloads_allowed"),
            description="Max downloads allowed parameter provided.",
        )

        cdk.CfnOutput(
            self,
            "AppSyncGraphQLURL",
            value=appsync_api.graphql_url,
            description="The URL for the endpoint in AppSync.",
        )

        cdk.CfnOutput(
            self,
            "CognitoUserPoolId",
            value=egress_user_pool.user_pool_id,
            description="The Id for the Cognito User Pool created.",
        )

        cdk.CfnOutput(
            self,
            "CognitoAppClientId",
            value=app_client.get_att("Ref").to_string(),
            description="The Id for the Cognito App client created.",
        )

        cdk.CfnOutput(
            self,
            "CognitoUserPoolDomain",
            value=f'{self.node.try_get_context(env_id).get("cognito_userpool_domain")}.auth.{self.region}.amazoncognito.com',
            description="The domain name for the Cognito User Pool created.",
        )

        cdk.CfnOutput(
            self,
            "EgressWebAppS3BucketName",
            value=egress_webapp_bucket.bucket_name,
            description="The name for the S3 bucket created to host the packaged frontend app.",
        )
