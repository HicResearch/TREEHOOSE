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


class EmailConfigurationSetCustomResource(cdk.Construct):
    """Construct to trigger the creation of an SES configuration set. Uses AWSCustomResource internally
    :param account_id -- The AWS Account ID
    :param region -- The deployment region
    :param env_id -- The environment ID
    :param configuration_set_name -- The name for the configuration set
    """

    def __init__(
        self,
        scope: cdk.Construct,
        id: str,  # noqa A002 default cdk construct
        account_id: str,
        region: str,
        env_id: str,
        configuration_set_name: str,
    ):
        super().__init__(scope, id)

        lambda_role = self.get_provisioning_lambda_role(construct_id=id)
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                resources=[
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/lambda/EgressAppBackend*"
                ],
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
            )
        )

        AwsCustomResource(
            scope=self,
            id=f"EmailConfigurationSetCustomResource-{env_id}",
            # Need to explicitly set the policy due to https://github.com/aws/aws-cdk/issues/4533
            policy=AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        resources=[
                            f"arn:aws:ses:{region}:{account_id}:configuration-set/{configuration_set_name}"
                        ],
                        actions=[
                            "ses:CreateConfigurationSet",
                            "ses:DeleteConfigurationSet",
                        ],
                    )
                ]
            ),
            log_retention=logs.RetentionDays.FIVE_DAYS,
            on_create=self.create(configuration_set_name),
            on_delete=self.delete(configuration_set_name),
            resource_type="Custom::EmailConfigurationSetCustomResource",
        )

    def create(self, configuration_set_name):

        create_params = {
            "ConfigurationSetName": configuration_set_name,
            "SendingOptions": {"SendingEnabled": True},
        }

        return AwsSdkCall(
            action="createConfigurationSet",
            service="SESV2",
            parameters=create_params,
            physical_resource_id=PhysicalResourceId.of(f"SES-{configuration_set_name}"),
        )

    def delete(self, configuration_set_name):

        delete_params = {"ConfigurationSetName": configuration_set_name}

        return AwsSdkCall(
            action="deleteConfigurationSet", service="SESV2", parameters=delete_params
        )

    def get_provisioning_lambda_role(self, construct_id: str):
        return iam.Role(
            scope=self,
            id=f"{construct_id}-LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
