# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
import os

from aws_cdk import Duration, Stack
from aws_cdk import aws_backup as backup
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as aws_lambda
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_stepfunctions as sf
from aws_cdk import aws_stepfunctions_tasks as sft
from aws_cdk.aws_logs import RetentionDays
from cdk_nag import NagSuppressions
from constructs import Construct

dirname = os.path.dirname(__file__)


class WorkspaceBackupInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define Lambda Powertools layer
        powertools_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            "rPowertoolsLayer",
            f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPython:{self.node.try_get_context('powertools_layer_version')}",  # noqa: E501
        )

        backup_settings = self.node.try_get_context("backup_settings")

        # Lambda Execution Permissions
        lambda_exec_policy = iam.ManagedPolicy(
            self,
            "rLambdaExecutionPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
                    resources=["*"],
                ),
            ],
        )

        # EBS Tagging Function role and policies
        tag_ebs_function_custom_policy = iam.ManagedPolicy(
            self,
            "rTagEbsFunctionCustomPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ec2:CreateTags",
                        "ec2:DescribeVolumes",
                        "ec2:DescribeInstances",
                    ],
                    resources=["*"],
                ),
            ],
        )

        tag_ebs_function_role = iam.Role(
            self,
            "rTagEbsFunctionRole",
            description="Role used by tag_ebs_function lambda function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        tag_ebs_function_role.add_managed_policy(lambda_exec_policy)
        tag_ebs_function_role.add_managed_policy(tag_ebs_function_custom_policy)

        # EBS Tagging Function
        tag_ebs_function = aws_lambda.Function(
            self,
            "rTagEbsFunction",
            description="This function tags ebs volumes attached to EC2 instances that need backup within the TRE environment",  # noqa: E501
            function_name="tag_ebs_function",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, "functions/tag_ebs")
            ),
            memory_size=128,
            timeout=Duration.seconds(30),
            role=tag_ebs_function_role,
            tracing=aws_lambda.Tracing.ACTIVE,
            log_retention=RetentionDays.SIX_MONTHS,
            layers=[powertools_layer],
            environment={
                "CHECK_BACKUP_TAG": json.dumps(
                    backup_settings.get("backup_tag").get("check")
                ),
                "ADD_BACKUP_TAG": json.dumps(
                    backup_settings.get("backup_tag").get("add")
                ),
            },
        )

        # Event rule to trigger ebs tagging
        events.Rule(
            self,
            "rInvokeEbsBackupTagging",
            description="Rule triggered when EC2 instance state changes to running. Target adds necesssary tags to EBS volume is backup is required for the TRE Workspace ",  # noqa E501
            event_pattern=events.EventPattern(
                source=["aws.ec2"],
                detail_type=["EC2 Instance State-change Notification"],
                detail={"state": ["running"]},
            ),
            targets=[targets.LambdaFunction(tag_ebs_function, retry_attempts=2)],
        )

        # Backup Plan
        backup_plan = backup.BackupPlan(self, "rBackupPlan")

        backup_plan.add_rule(
            backup.BackupPlanRule(
                delete_after=Duration.days(
                    backup_settings.get("retention_period").get("days")
                ),
                move_to_cold_storage_after=Duration.days(
                    backup_settings.get("move_to_cold_storage_after").get("days")
                ),
                schedule_expression=events.Schedule.expression(
                    f"cron({backup_settings.get('backup_schedule').get('cloudwatch_cron').get(backup_settings.get('frequency'))})"  # noqa: E501
                ),
                start_window=Duration.minutes(60),
                completion_window=Duration.minutes(600),
            )
        )

        backup_plan.add_selection(
            "rVolumeBackup",
            resources=[
                backup.BackupResource.from_tag(
                    backup_settings.get("backup_tag").get("add").get("Key"),
                    backup_settings.get("backup_tag").get("add").get("Value"),
                )
            ],
            allow_restores=True,
        )

        # S3 Access Logs Bucket
        s3_access_logs_bucket = s3.Bucket(
            self,
            "rS3AccessLogsBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f"sagemaker-backup-s3-access-logs-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
        )

        # Lifecycle rule to delete S3 access logs after retention period
        s3_access_logs_bucket.add_lifecycle_rule(
            id="rS3AccessLogsRetention",
            enabled=True,
            expiration=Duration.days(
                backup_settings.get("retention_period").get("days")
            ),
        )

        # S3 backup bucket for Sagemaker notebooks
        sagemaker_backup_bucket = s3.Bucket(
            self,
            "rSagemakerBackupBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f"sagemeker-backup-bucket-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            public_read_access=False,
            server_access_logs_bucket=s3_access_logs_bucket,
            server_access_logs_prefix=f"sagemeker-backup-bucket-{self.account}-{self.region}/",  # noqa: E501
        )

        # Lifecycle rule to transition old backups to cold storage
        sagemaker_backup_bucket.add_lifecycle_rule(
            id="transition-to-cold-storage",
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=Duration.days(
                        backup_settings.get("move_to_cold_storage_after").get("days")
                    ),
                )
            ],
            noncurrent_version_transitions=[
                s3.NoncurrentVersionTransition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=Duration.days(
                        backup_settings.get("move_to_cold_storage_after").get("days")
                    ),
                )
            ],
        )

        # Lifecycle rule to apply data retention on backups
        sagemaker_backup_bucket.add_lifecycle_rule(
            id="apply-backup-retention",
            expiration=Duration.days(
                backup_settings.get("retention_period").get("days")
            ),
        )
        sagemaker_backup_bucket.add_lifecycle_rule(
            id="delete-noncurrent-files",
            expired_object_delete_marker=True,
            noncurrent_version_expiration=Duration.days(
                backup_settings.get("retention_period").get("days")
            ),
        )

        # Lifecycle rule to delete incomplete multi-part uploads
        sagemaker_backup_bucket.add_lifecycle_rule(
            id="delete-incomplete-mpus",
            abort_incomplete_multipart_upload_after=Duration.days(1),
        )

        # Lambda layer for common utils
        utils_layer = aws_lambda.LayerVersion(
            self,
            "rUtilsLayer",
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, "./lambda_layer/")
            ),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
        )

        # Sagemaker notebook info function role and policies
        get_sagemaker_notebook_info_function_custom_policy = iam.ManagedPolicy(
            self,
            "rGetSagemakerNotebookInfoFunctionCustomPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "iam:CreatePolicy",
                        "iam:AttachRolePolicy",
                        "iam:TagPolicy",
                    ],
                    resources=[
                        f"arn:aws:iam::{self.account}:role/*sagemaker-notebook-role",
                        f"arn:aws:iam::{self.account}:policy/sagemaker-backup-policy-for*",
                        f"arn:aws:iam::{self.account}:policy/sagemaker-restore-policy-for*",
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sagemaker:DescribeNotebookInstanceLifecycleConfig",
                        "sagemaker:UpdateNotebookInstanceLifecycleConfig",
                    ],
                    resources=[
                        f"arn:aws:sagemaker:*:{self.account}:notebook-instance-lifecycle-config/BasicNotebookInstanceLifecycleConfig*",
                    ],
                ),
            ],
        )

        get_sagemaker_notebook_info_function_role = iam.Role(
            self,
            "rGetSagemakerNotebookInfoFunctionRole",
            description="Role used by get_sagemaker_notebook_info_function lambda function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        get_sagemaker_notebook_info_function_role.add_managed_policy(lambda_exec_policy)
        get_sagemaker_notebook_info_function_role.add_managed_policy(
            get_sagemaker_notebook_info_function_custom_policy
        )

        sagemaker_backup_bucket.grant_put(get_sagemaker_notebook_info_function_role)

        # Function to get Sagemaker notebook info and create S3 prefix
        get_sagemaker_notebook_info_function = aws_lambda.Function(
            self,
            "rGetSagemakerNotebookInfoFunction",
            description="This function retrieves SageMaker notebook info",
            function_name="get_sagemaker_notebook_info_function",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, "functions/get_sagemaker_notebook_info")
            ),
            memory_size=128,
            timeout=Duration.seconds(30),
            role=get_sagemaker_notebook_info_function_role,
            tracing=aws_lambda.Tracing.ACTIVE,
            log_retention=RetentionDays.SIX_MONTHS,
            layers=[powertools_layer],
            environment={
                "BACKUP_BUCKET": sagemaker_backup_bucket.bucket_name,
                "BACKUP_TAG": json.dumps(
                    backup_settings.get("backup_tag").get("check")
                ),
                "ACCOUNT": self.account,
                "BACKUP_SCHEDULE": backup_settings.get("backup_schedule")
                .get("unix_crontab")
                .get(backup_settings.get("frequency")),
            },
        )

        # Retrieve CloudFormation stack status function role and policies
        retrieve_stack_status_function_custom_policy = iam.ManagedPolicy(
            self,
            "rRetrieveStackStatusFunctionCustomPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudformation:DescribeStacks",
                    ],
                    resources=[
                        f"arn:aws:cloudformation:*:{self.account}:stack/SC-*/*",
                    ],
                ),
            ],
        )

        retrieve_stack_status_function_role = iam.Role(
            self,
            "rRetrieveStackStatusFunctionRole",
            description="Role used by retrieve_stack_status lambda function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        retrieve_stack_status_function_role.add_managed_policy(lambda_exec_policy)
        retrieve_stack_status_function_role.add_managed_policy(
            retrieve_stack_status_function_custom_policy
        )

        # Retrieve CloudFormation stack status function
        retrieve_stack_status_function = aws_lambda.Function(
            self,
            "rRetrieveStackStatusFunction",
            description="This function retrieves the stack status for Notebook creation",
            function_name="retrieve_stack_status_function",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, "functions/retrieve_stack_status")
            ),
            memory_size=128,
            timeout=Duration.seconds(30),
            role=retrieve_stack_status_function_role,
            tracing=aws_lambda.Tracing.ACTIVE,
            log_retention=RetentionDays.SIX_MONTHS,
            layers=[powertools_layer],
            environment={},
        )

        # Role and policies for function to enable backup in SageMaker notebook
        enable_sagemaker_backup_function_custom_policy = iam.ManagedPolicy(
            self,
            "rEnableSageMakerBackupFunctionCustomPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudformation:DescribeStacks",
                        "cloudformation:GetTemplate",
                        "cloudformation:CreateChangeSet",
                        "cloudformation:ExecuteChangeSet",
                        "cloudformation:DescribeChangeSet",
                    ],
                    resources=[
                        f"arn:aws:cloudformation:*:{self.account}:stack/SC-*/*",
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["ec2:DescribeVpcs", "ec2:DescribeSubnets"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "iam:PutRolePolicy",
                        "iam:DeleteRolePolicy",
                        "iam:GetRolePolicy",
                        "iam:GetRole",
                    ],
                    resources=[
                        f"arn:aws:iam::{self.account}:role/*sagemaker-notebook-role"
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sagemaker:DescribeNotebookInstanceLifecycleConfig",
                        "sagemaker:DescribeNotebookInstance",
                        "sagemaker:UpdateNotebookInstanceLifecycleConfig",
                    ],
                    resources=[
                        f"arn:aws:sagemaker:*:{self.account}:notebook-instance-lifecycle-config/BasicNotebookInstanceLifecycleConfig*",
                        f"arn:aws:sagemaker:*:{self.account}:notebook-instance/basicnotebookinstance-*",  # noqa: E501
                    ],
                ),
            ],
        )

        enable_sagemaker_backup_function_role = iam.Role(
            self,
            "rEnableSageMakerBackupFunctionRole",
            description="Role used by enable_sagemaker_backup_function lambda function",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        enable_sagemaker_backup_function_role.add_managed_policy(lambda_exec_policy)
        enable_sagemaker_backup_function_role.add_managed_policy(
            enable_sagemaker_backup_function_custom_policy
        )

        # Function to update Sagemaker notebook stack to enable backups
        enable_sagemaker_backup_function = aws_lambda.Function(
            self,
            "rEnableSageMakerBackupFunction",
            description="This function updates SageMaker notebook lifecycle policy to add backup script",  # noqa: E501
            function_name="enable_sagemaker_backup_function",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, "functions/enable_sagemaker_backup")
            ),
            memory_size=128,
            timeout=Duration.seconds(60),
            role=enable_sagemaker_backup_function_role,
            tracing=aws_lambda.Tracing.ACTIVE,
            log_retention=RetentionDays.SIX_MONTHS,
            layers=[powertools_layer, utils_layer],
            environment={
                "BACKUP_BUCKET": sagemaker_backup_bucket.bucket_name,
                "BACKUP_SCHEDULE": backup_settings.get("backup_schedule")
                .get("unix_crontab")
                .get(backup_settings.get("frequency")),
                "ENABLE_RESTORE": backup_settings.get(
                    "sagemaker_enable_selfservice_restore"
                ),
            },
        )

        # State machine jobs
        get_sagemaker_notebook_info_job = sft.LambdaInvoke(
            self,
            "Get Sagemaker instance notebook info",
            lambda_function=get_sagemaker_notebook_info_function,
            output_path="$.Payload",
        )

        retrieve_stack_creation_status_job = sft.LambdaInvoke(
            self,
            "Retrieve Stack Creation Status",
            lambda_function=retrieve_stack_status_function,
            output_path="$.Payload",
        )

        retrieve_stack_update_status_job = sft.LambdaInvoke(
            self,
            "Retrieve Stack Update Status",
            lambda_function=retrieve_stack_status_function,
            output_path="$.Payload",
        )

        enable_sagemaker_backup_job = sft.LambdaInvoke(
            self,
            "Enable backup script",
            comment="Executes Cloudformation stackset to enable backup script",
            lambda_function=enable_sagemaker_backup_function,
            output_path="$.Payload",
        )

        stack_creation_wait_job = sf.Wait(
            self,
            "Wait 30 Seconds for stack creation",
            time=sf.WaitTime.duration(Duration.seconds(30)),
        )

        stack_update_wait_job = sf.Wait(
            self,
            "Wait 30 Seconds for stack updates",
            time=sf.WaitTime.duration(Duration.seconds(30)),
        )

        pass_job = sf.Pass(self, "Pass", comment="Does not need a backup setup")
        fail_job = sf.Fail(self, "Fail", comment="Backup configuration failed")

        sagemaker_stack_creation_wait_defintion = stack_creation_wait_job.next(
            retrieve_stack_creation_status_job
        )
        sagemaker_changeset_wait_defintion = stack_update_wait_job.next(
            retrieve_stack_update_status_job
        )

        # State machine sub-routine for check stack update status
        sagemaker_update_loop_defintion = enable_sagemaker_backup_job.next(
            retrieve_stack_update_status_job
        ).next(
            sf.Choice(self, "Is Notebook Stack Updated?")
            .when(
                sf.Condition.string_equals("$.stack_status", "UPDATE_COMPLETE"),
                pass_job,
            )
            .otherwise(sagemaker_changeset_wait_defintion)
        )

        # State machine sub-routine for check stack creation status
        sagemaker_creation_loop_defintion = retrieve_stack_creation_status_job.next(
            sf.Choice(self, "Is Notebook Stack Created?")
            .when(
                sf.Condition.string_equals("$.stack_status", "CREATE_COMPLETE"),
                sagemaker_update_loop_defintion,
            )
            .when(
                sf.Condition.string_equals("$.stack_status", "ROLLBACK_IN_PROGRESS"),
                fail_job,
            )
            .when(
                sf.Condition.string_equals("$.stack_status", "CREATE_FAILED"), fail_job
            )
            .otherwise(sagemaker_stack_creation_wait_defintion)
        )

        # State machine for sagemaker backups
        sagemaker_backup_sf_defintion = get_sagemaker_notebook_info_job.next(
            sf.Choice(self, "Is Backup Required?")
            .when(
                sf.Condition.boolean_equals("$.notebook_backup_enabled", False),
                pass_job,
            )
            .otherwise(sagemaker_creation_loop_defintion)
        )

        # State machine log group
        sagemaker_notebook_backup_log_group = logs.LogGroup(
            self,
            "rSageMakerNotebookBackupSfLg",
            retention=logs.RetentionDays.SIX_MONTHS,
        )

        # Create state machine
        sagemaker_notebook_backup_sf = sf.StateMachine(
            self,
            "rSageMakerNotebookBackupStepFunction",
            definition=sagemaker_backup_sf_defintion,
            timeout=Duration.minutes(20),
            tracing_enabled=True,
            logs=sf.LogOptions(
                destination=sagemaker_notebook_backup_log_group, level=sf.LogLevel.ALL
            ),
        )

        # Role for allowing EventBridge rule to trigger State Machine
        state_machine_invoke_role = iam.Role(
            self,
            "rStateMachineInvokeRole",
            assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
        )

        # Event rule to trigger Sagemaker notebook backup setup
        events.Rule(
            self,
            "rInvokeSageMakerNotebookBackupTagging",
            description="Rule triggered when Sagemaker notebook is created. Target updates the notebook lifecyle hook to schedule backups",
            event_pattern=events.EventPattern(
                source=["aws.sagemaker"],
                detail_type=["AWS API Call via CloudTrail"],
                detail={
                    "eventSource": ["sagemaker.amazonaws.com"],
                    "eventName": ["CreateNotebookInstance"],
                },
            ),
            targets=[
                targets.SfnStateMachine(
                    sagemaker_notebook_backup_sf,
                    role=state_machine_invoke_role,
                    retry_attempts=2,
                )
            ],
        )

        # CDK-NAG suppressions with explaination
        NagSuppressions.add_resource_suppressions(
            lambda_exec_policy,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "need wildcard to create log group and stream logs",
                }
            ],
        )

        NagSuppressions.add_resource_suppressions_by_path(
            self,
            path="/WorkspaceBackupInfrastructureStack/rBackupPlan/rVolumeBackup/Role/Resource",
            suppressions=[
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "Using service roles \
                        AWSBackupServiceRolePolicyForBackup and AWSBackupServiceRolePolicyForRestores for backups and restores",
                },
            ],
        )

        NagSuppressions.add_resource_suppressions_by_path(
            self,
            path="/WorkspaceBackupInfrastructureStack/LogRetentionaae0aa3c5b4d4f87b02d85b201efdd8a/ServiceRole",
            suppressions=[
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": "AWSLambdaBasicExecutionRole used by default cdk lambda construct \
                        that adds log retention",
                },
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "AWSLambdaBasicExecutionRole used by default cdk lambda construct \
                        that adds log retention",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            tag_ebs_function_custom_policy,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Needs access on all resources as\
                        specific resources created by TRE are unknown.",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            get_sagemaker_notebook_info_function_role,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Lambda execution policy provides access to all\
                        log groups and x-ray trace for creating streams and traces",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            get_sagemaker_notebook_info_function_custom_policy,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Restricted to resource naming pattern\
                        created by TRE. Cannot restrict further.",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            tag_ebs_function_role,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Lambda execution policy provides access to all\
                        log groups and x-ray trace for creating streams and traces",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            enable_sagemaker_backup_function_role,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Lambda execution policy provides access to all\
                        log groups and x-ray trace for creating streams and traces",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            enable_sagemaker_backup_function_custom_policy,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Restricted to resource naming pattern\
                        created by TRE. Cannot restrict further.",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            retrieve_stack_status_function_custom_policy,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Restricted to resource naming pattern\
                        created by TRE. Cannot restrict further.",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            retrieve_stack_status_function_role,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Lambda execution policy provides access to all\
                        log groups and x-ray trace for creating streams and traces",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            sagemaker_notebook_backup_sf,
            suppressions=[
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Provides access to deliver logs and traces",
                },
            ],
            apply_to_children=True,
        )

        NagSuppressions.add_resource_suppressions(
            s3_access_logs_bucket,
            suppressions=[
                {
                    "id": "AwsSolutions-S1",
                    "reason": "This bucket is target for server access logs",
                }
            ],
        )
