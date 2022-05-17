import json

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Match, Template

from src.workspace_backup_infrastructure_stack import WorkspaceBackupInfrastructureStack

CONTEXT = {
    "powertools_layer_version": "16",
    "backup_settings": {
        "frequency": "hourly",
        "backup_tag": {
            "check": {"Key": "backup", "Value": "true"},
            "add": {"Key": "backupVolume", "Value": "true"},
        },
        "backup_schedule": {
            "cloudwatch_cron": {"hourly": "0 * ? * * *", "daily": "0 0 ? * * *"},
            "unix_crontab": {"hourly": "0 * * * *", "daily": "0 0 * * *"},
        },
        "retention_period": {"days": 180},
        "move_to_cold_storage_after": {"days": 90},
        "sagemaker_enable_selfservice_restore": "true",
    },
}


@pytest.fixture()
def app():
    return cdk.App(context=CONTEXT)


@pytest.fixture()
def stack():
    app = cdk.App(context=CONTEXT)

    return WorkspaceBackupInfrastructureStack(app, "WorkspaceBackupInfrastructureStack")


@pytest.fixture()
def template():
    app = cdk.App(context=CONTEXT)

    workspace_backup_infrastructure_stack = WorkspaceBackupInfrastructureStack(
        app, "WorkspaceBackupInfrastructureStack"
    )

    return Template.from_stack(workspace_backup_infrastructure_stack)


def test_stack_compiling(stack):
    Template.from_stack(stack)


def test_resource_counts(template):
    template.resource_count_is("AWS::IAM::ManagedPolicy", 5)
    template.resource_count_is("AWS::IAM::Role", 8)
    template.resource_count_is("AWS::IAM::Policy", 7)
    template.resource_count_is("AWS::Lambda::Function", 5)
    template.resource_count_is("AWS::Backup::BackupSelection", 1)
    template.resource_count_is("AWS::Backup::BackupPlan", 1)
    template.resource_count_is("AWS::Backup::BackupVault", 1)
    template.resource_count_is("AWS::S3::Bucket", 2)
    template.resource_count_is("AWS::S3::BucketPolicy", 2)
    template.resource_count_is("AWS::StepFunctions::StateMachine", 1)
    template.resource_count_is("AWS::Events::Rule", 2)


def test_backup_plan_config(template):
    backup_cron = CONTEXT["backup_settings"]["backup_schedule"]["cloudwatch_cron"][
        CONTEXT["backup_settings"]["frequency"]
    ]
    template.has_resource_properties(  # noqa ECE001 backup plan config is complex
        "AWS::Backup::BackupPlan",
        {
            "BackupPlan": {
                "BackupPlanName": "rBackupPlan",
                "BackupPlanRule": [
                    {
                        "CompletionWindowMinutes": 600,
                        "Lifecycle": {
                            "DeleteAfterDays": CONTEXT["backup_settings"][
                                "retention_period"
                            ]["days"],
                            "MoveToColdStorageAfterDays": CONTEXT["backup_settings"][
                                "move_to_cold_storage_after"
                            ]["days"],
                        },
                        "RuleName": "rBackupPlanRule0",
                        "ScheduleExpression": f"cron({backup_cron})",
                        "StartWindowMinutes": 60,
                        "TargetBackupVault": Match.any_value(),
                    }
                ],
            }
        },
    )


def test_backup_backupselection_config(template):
    template.has_resource_properties(
        "AWS::Backup::BackupSelection",
        {
            "BackupPlanId": Match.any_value(),
            "BackupSelection": {
                "IamRoleArn": Match.any_value(),
                "ListOfTags": [
                    {
                        "ConditionKey": CONTEXT["backup_settings"]["backup_tag"]["add"][
                            "Key"
                        ],
                        "ConditionType": "STRINGEQUALS",
                        "ConditionValue": CONTEXT["backup_settings"]["backup_tag"][
                            "add"
                        ]["Value"],
                    }
                ],
                "SelectionName": "rVolumeBackup",
            },
        },
    )


def test_volume_backup_event_rule_config(template):
    template.has_resource_properties(
        "AWS::Events::Rule",
        {
            "EventPattern": {
                "detail": {"state": ["running"]},
                "detail-type": ["EC2 Instance State-change Notification"],
                "source": ["aws.ec2"],
            }
        },
    )


def test_sagemaker_notebook_backup_event_rule_config(template):
    template.has_resource_properties(
        "AWS::Events::Rule",
        {
            "EventPattern": {
                "detail": {
                    "eventSource": ["sagemaker.amazonaws.com"],
                    "eventName": ["CreateNotebookInstance"],
                },
                "detail-type": ["AWS API Call via CloudTrail"],
                "source": ["aws.sagemaker"],
            },
        },
    )


def test_tag_ebs_function(template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Code": {
                "S3Bucket": Match.any_value(),
                "S3Key": Match.any_value(),
            },
            "Role": Match.any_value(),
            "Description": "This function tags ebs volumes attached to EC2 instances that need backup within the TRE environment",
            "Environment": {
                "Variables": {
                    "CHECK_BACKUP_TAG": json.dumps(
                        CONTEXT["backup_settings"]["backup_tag"]["check"]
                    ),
                    "ADD_BACKUP_TAG": json.dumps(
                        CONTEXT["backup_settings"]["backup_tag"]["add"]
                    ),
                }
            },
            "FunctionName": "tag_ebs_function",
            "Handler": "lambda_function.lambda_handler",
            "MemorySize": 128,
            "Runtime": "python3.8",
            "Timeout": 30,
            "TracingConfig": {"Mode": "Active"},
        },
    )


def test_get_sagemaker_notebook_info_function(template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Code": {
                "S3Bucket": Match.any_value(),
                "S3Key": Match.any_value(),
            },
            "Role": Match.any_value(),
            "Description": "This function retrieves SageMaker notebook info",
            "Environment": {
                "Variables": {
                    "BACKUP_BUCKET": {"Ref": "rSagemakerBackupBucket8178ADBC"},
                    "BACKUP_TAG": json.dumps(
                        CONTEXT["backup_settings"]["backup_tag"]["check"]
                    ),
                    "ACCOUNT": {"Ref": "AWS::AccountId"},
                    "BACKUP_SCHEDULE": CONTEXT["backup_settings"]["backup_schedule"][
                        "unix_crontab"
                    ][CONTEXT["backup_settings"]["frequency"]],
                }
            },
            "FunctionName": "get_sagemaker_notebook_info_function",
            "Handler": "lambda_function.lambda_handler",
            "MemorySize": 128,
            "Runtime": "python3.8",
            "Timeout": 30,
            "TracingConfig": {"Mode": "Active"},
        },
    )


def test_retrieve_stack_status_function(template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Code": {
                "S3Bucket": Match.any_value(),
                "S3Key": Match.any_value(),
            },
            "Role": Match.any_value(),
            "Description": "This function retrieves the stack status for Notebook creation",
            "FunctionName": "retrieve_stack_status_function",
            "Handler": "lambda_function.lambda_handler",
            "MemorySize": 128,
            "Runtime": "python3.8",
            "Timeout": 30,
            "TracingConfig": {"Mode": "Active"},
        },
    )


def test_enable_sagemaker_backup_function(template):
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Code": {
                "S3Bucket": Match.any_value(),
                "S3Key": Match.any_value(),
            },
            "Role": Match.any_value(),
            "Description": "This function updates SageMaker notebook lifecycle policy to add backup script",
            "Environment": {
                "Variables": {
                    "ENABLE_RESTORE": CONTEXT["backup_settings"][
                        "sagemaker_enable_selfservice_restore"
                    ],
                    "BACKUP_SCHEDULE": CONTEXT["backup_settings"]["backup_schedule"][
                        "unix_crontab"
                    ][CONTEXT["backup_settings"]["frequency"]],
                }
            },
            "FunctionName": "enable_sagemaker_backup_function",
            "Handler": "lambda_function.lambda_handler",
            "MemorySize": 128,
            "Runtime": "python3.8",
            "Timeout": 60,
            "TracingConfig": {"Mode": "Active"},
        },
    )
