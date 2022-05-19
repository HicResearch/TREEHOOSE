# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os
import time
import uuid

import boto3
import yaml
from aws_lambda_powertools import Logger, Metrics, Tracer

tracer = Tracer(service="TRESageMakerEnableBackupFunction")
logger = Logger(service="TRESageMakerEnableBackupFunction", sample_rate=0.1)
metrics = Metrics(
    service="TRESageMakerEnableBackupFunction",
    namespace="TREBackups",
)

BACKUP_BUCKET = os.environ["BACKUP_BUCKET"]
BACKUP_SCHEDULE = os.environ["BACKUP_SCHEDULE"]
ENABLE_RESTORE = os.environ["ENABLE_RESTORE"]

cfn_client = boto3.client("cloudformation")


def lambda_handler(event, context):
    logger.info(event)

    notebook_name = event["notebook_name"]
    notebook_cfn_stack_name = event["notebook_cfn_stack_name"]

    describe_stack_response = cfn_client.describe_stacks(
        StackName=notebook_cfn_stack_name,
    )

    logger.info(describe_stack_response)

    backup_policy_document_cfn = {
        "Type": "AWS::IAM::Policy",
        "Properties": {
            "PolicyName": f"sagemaker-backup-policy-for-{notebook_name}",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:ListBucket"],
                        "Resource": f"arn:aws:s3:::{BACKUP_BUCKET}",
                        "Condition": {"StringEquals": {"s3:prefix": notebook_name}},
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["s3:PutObject"],
                        "Resource": [f"arn:aws:s3:::{BACKUP_BUCKET}/{notebook_name}/*"],
                    },
                ],
            },
            "Roles": [{"Ref": "IAMRole"}],
        },
    }

    get_template_response = cfn_client.get_template(
        StackName=notebook_cfn_stack_name, TemplateStage="Original"
    )

    logger.info(get_template_response)

    existing_template = yaml.full_load(get_template_response.get("TemplateBody"))

    existing_template["Resources"]["S3BackupPolicy"] = backup_policy_document_cfn
    if [ENABLE_RESTORE.lower() == "true"]:
        restore_policy_document_cfn = {
            "Type": "AWS::IAM::Policy",
            "Properties": {
                "PolicyName": f"sagemaker-restore-policy-for-{notebook_name}",
                "PolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["s3:ListBucket"],
                            "Resource": [
                                f"arn:aws:s3:::{BACKUP_BUCKET}/{notebook_name}"
                            ],
                            "Condition": {"StringEquals": {"s3:prefix": notebook_name}},
                        },
                        {
                            "Effect": "Allow",
                            "Action": ["s3:GetObject", "s3:GetObjectVersion"],
                            "Resource": [
                                f"arn:aws:s3:::{BACKUP_BUCKET}/{notebook_name}/*"
                            ],
                        },
                    ],
                },
                "Roles": [{"Ref": "IAMRole"}],
            },
        }
        existing_template["Resources"]["S3RestorePolicy"] = restore_policy_document_cfn

    script = existing_template["Resources"]["BasicNotebookInstanceLifecycleConfig"][
        "Properties"
    ]["OnStart"][0]["Content"]["Fn::Base64"]["Fn::Sub"]
    new_script = f"""{script}
# new parts of script below here
cat << "EOF" > /tmp/backup.sh
#!/usr/bin/env bash
echo "Starting the SageMaker backup script"
aws s3 cp --recursive --exclude "lost+found/*" --exclude "studies/*" /home/ec2-user/SageMaker/ s3://{BACKUP_BUCKET}/{notebook_name}/
echo "Completed the SageMaker backup script"
EOF
chmod +x /tmp/backup.sh
(crontab -l 2>/dev/null; echo "{BACKUP_SCHEDULE} /tmp/backup.sh >> /var/log/backup.log") | crontab -
/tmp/backup.sh"""

    existing_template["Resources"]["BasicNotebookInstanceLifecycleConfig"][
        "Properties"
    ]["OnStart"][0]["Content"]["Fn::Base64"]["Fn::Sub"] = new_script
    updated_template = yaml.dump(existing_template)

    create_change_set_response = cfn_client.create_change_set(
        StackName=notebook_cfn_stack_name,
        TemplateBody=updated_template,
        Parameters=[
            {"ParameterKey": "EncryptionKeyArn", "UsePreviousValue": True},
            {"ParameterKey": "VPC", "UsePreviousValue": True},
            {"ParameterKey": "S3Mounts", "UsePreviousValue": True},
            {"ParameterKey": "IamPolicyDocument", "UsePreviousValue": True},
            {"ParameterKey": "EnvironmentInstanceFiles", "UsePreviousValue": True},
            {"ParameterKey": "InstanceType", "UsePreviousValue": True},
            {"ParameterKey": "Subnet", "UsePreviousValue": True},
            {"ParameterKey": "AutoStopIdleTimeInMinutes", "UsePreviousValue": True},
            {"ParameterKey": "IsAppStreamEnabled", "UsePreviousValue": True},
            {"ParameterKey": "EgressStoreIamPolicyDocument", "UsePreviousValue": True},
            {"ParameterKey": "SolutionNamespace", "UsePreviousValue": True},
            {"ParameterKey": "AccessFromCIDRBlock", "UsePreviousValue": True},
            {"ParameterKey": "Namespace", "UsePreviousValue": True},
        ],
        Capabilities=[
            "CAPABILITY_NAMED_IAM",
        ],
        ChangeSetName="backupchangeset",
        Description="this changes the sagemaker cloudformation template so it can be deleted after changes associated with backup",
        ChangeSetType="UPDATE",
    )
    logger.info("Change set created for notebook %s", notebook_name)
    logger.debug(create_change_set_response)

    describe_change_set_response = cfn_client.describe_change_set(
        ChangeSetName="backupchangeset",
        StackName=notebook_cfn_stack_name,
    )

    current_status = describe_change_set_response["Status"]

    while current_status != "CREATE_COMPLETE":

        describe_change_set_response = cfn_client.describe_change_set(
            ChangeSetName="backupchangeset",
            StackName=notebook_cfn_stack_name,
        )

        current_status = describe_change_set_response["Status"]

        time.sleep(5)

    execute_change_set_response = cfn_client.execute_change_set(
        ChangeSetName="backupchangeset",
        StackName=notebook_cfn_stack_name,
        ClientRequestToken=str(uuid.uuid4()),
        DisableRollback=False,
    )
    logger.info("Change set execution started for notebook %s", notebook_name)

    logger.info(execute_change_set_response)

    return event
