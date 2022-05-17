# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
import os

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.data_classes import SNSEvent, event_source

tracer = Tracer(service="TriggerEgressWorkflow")
logger = Logger(service="TriggerEgressWorkflow", sample_rate=0.1)
metrics = Metrics(service="TriggerEgressWorkflow", namespace="EgressRequests")

step_fn_client = boto3.client('stepfunctions')

egress_workflow_step_fn_arn = os.environ['STEP_FUNCTION_ARN']
reviewer_list = os.environ['REVIEWER_LIST']
egress_app_url = os.environ['EGRESS_APP_URL']
tre_admin_email_address = os.environ['EGRESS_APP_ADMIN_EMAIL']


@metrics.log_metrics()
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@event_source(data_class=SNSEvent)
def handler(event: SNSEvent, context):
    for record in event.records:
        message = record.sns.message
        start_egress_workflow(json.loads(message))

    metrics.add_metric(name="EgressRequestSubmitted", value=1, unit=MetricUnit.Count)


def start_egress_workflow(message):
    logger.info(json.dumps(message))

    message["egress_request_id"] = message["id"]
    message["status"] = "PROCESSING"
    message["ver"] = str(message["ver"])
    message["reviewer_list"] = json.loads(reviewer_list)
    message["egress_app_url"] = egress_app_url
    message["tre_admin_email_address"] = tre_admin_email_address

    logger.info('Starting workflow with egress request ID: ' + message["egress_request_id"])

    step_fn_client.start_execution(
        stateMachineArn=egress_workflow_step_fn_arn,
        name=message["egress_request_id"],
        input=json.dumps(message)
    )
