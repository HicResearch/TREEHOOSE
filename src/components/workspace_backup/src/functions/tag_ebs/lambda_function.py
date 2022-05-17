import json
import os

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer

tracer = Tracer(service="TREEbsBackupFunction")
logger = Logger(service="TREEbsBackupFunction", sample_rate=0.1)
metrics = Metrics(
    service="TREEbsBackupFunction",
    namespace="TREBackups",
)

ec2 = boto3.resource("ec2")

CHECK_BACKUP_TAG = json.loads(os.environ["CHECK_BACKUP_TAG"])
ADD_BACKUP_TAG = json.loads(os.environ["ADD_BACKUP_TAG"])


def lambda_handler(event, context):
    instance_id = event["detail"]["instance-id"]
    instance = ec2.Instance(instance_id)

    if CHECK_BACKUP_TAG not in instance.tags:
        logger.info("backup tag not found on instance %s", instance_id)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"backup tag not found on instance {instance_id}"}
            ),
        }

    logger.info("backup tag found on instance %s", instance_id)
    for volume in instance.volumes.all():
        volume.create_tags(
            Tags=[ADD_BACKUP_TAG, {"Key": "instanceId", "Value": instance_id}]
        )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": f"backup tag added to EBS volumes for {instance_id}"}
        ),
    }
