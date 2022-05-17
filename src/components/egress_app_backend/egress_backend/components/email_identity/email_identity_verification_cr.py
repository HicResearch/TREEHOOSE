# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import core as cdk
from aws_cdk.custom_resources import (
    AwsCustomResource,
    AwsCustomResourcePolicy,
    AwsSdkCall,
    PhysicalResourceId,
)


class EmailIdentityVerificationCustomResource(cdk.Construct):
    """Construct to trigger a verification of an email identity. Uses AWSCustomResource internally
        :param account_id -- The AWS account number being deployed to
        :param region -- The AWS region being deployed to
        :param env_id -- The environment ID
        :param ses_sender_email -- The Email address the will be used as the "From" email for all outbound emails from SES
        :param configuration_set_name: The name of the default configuration set to apply to this verified email identity
    """

    def __init__(self, scope: cdk.Construct, id: str, account_id: str, region: str, env_id: str, ses_sender_email: str, configuration_set_name: str):
        super().__init__(scope, id)

        lambda_role = self.get_provisioning_lambda_role(construct_id=id)
        lambda_role.add_to_policy(iam.PolicyStatement(
            resources=[f"arn:aws:logs:{region}:{account_id}:log-group:/aws/lambda/EgressBackend*"],
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        ))

        AwsCustomResource(
            scope=self,
            id=f"EmailIdentityVerificationCustomResource-{env_id}",
            # Need to explicitly set the policy due to https://github.com/aws/aws-cdk/issues/4533
            policy=AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    resources=[f'arn:aws:ses:{region}:{account_id}:identity/{ses_sender_email}'],
                    actions=[
                        "ses:CreateEmailIdentity",
                        "ses:DeleteEmailIdentity"
                    ]
                )
            ]),
            log_retention=logs.RetentionDays.FIVE_DAYS,
            on_create=self.create(ses_sender_email, configuration_set_name),
            on_delete=self.delete(ses_sender_email),
            resource_type='Custom::EmailIdentityVerificationCustomResource'
        )

    def create(self, ses_sender_email, configuration_set_name):

        create_params = {
            "EmailIdentity": ses_sender_email,
            "ConfigurationSetName": configuration_set_name
        }

        return AwsSdkCall(
            action='createEmailIdentity',
            service='SESV2',
            parameters=create_params,
            physical_resource_id=PhysicalResourceId.of(f"verify-{ses_sender_email}")
        )

    def delete(self, ses_sender_email):

        delete_params = {
            "EmailIdentity": ses_sender_email
        }

        return AwsSdkCall(
            action='deleteEmailIdentity',
            service='SESV2',
            parameters=delete_params,
            physical_resource_id=PhysicalResourceId.of(f"verify-{ses_sender_email}")
        )

    def get_provisioning_lambda_role(self, construct_id: str):
        return iam.Role(
            scope=self,
            id=f'{construct_id}-LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
