# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
import os
from typing import Any

import boto3
from aws_lambda_powertools import Logger, Tracer
from boto3.dynamodb.conditions import Key

tracer = Tracer(service="UpdateRequestsAPI")
logger = Logger(service="UpdateRequestsAPI")

step_fn_client = boto3.client("stepfunctions")
ddb = boto3.resource("dynamodb")

egress_workflow_step_fn_arn = os.environ["STEP_FUNCTION_ARN"]
table = os.environ["TABLE"]
reviewer_list = os.environ["REVIEWER_LIST"]


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def update_request(arguments: str, context: Any):

    # Get the task token and id from the request
    inbound_egress_request_id = arguments["request"]["egress_request_id"]
    inbound_task_token = arguments["request"]["task_token"]
    usergroup = arguments["request"]["usergroup"]

    logger.info(
        "Update Request API invoked with Egress Request ID: %s",
        inbound_egress_request_id,
    )

    # Check if egress request is valid and retrieve details
    egress_details = retrieve_request_details(inbound_egress_request_id)

    # Check if reviewer is valid
    reviewer_valid = is_reviewer_valid(
        request_id=inbound_egress_request_id,
        reviewer_usergroup=usergroup,
        egress_request=egress_details,
    )

    # Check if request is valid
    request_valid = is_request_valid(
        request_id=inbound_egress_request_id,
        task_token=inbound_task_token,
        egress_request=egress_details,
    )

    # Determine egress request status and SWB status
    statuses = determine_status(
        egress_arguments=arguments, reviewer_usergroup=usergroup
    )

    # Append appropriate fields to arguments for SFN audit
    arguments["request"]["egress_status"] = statuses["egress_status"]
    arguments["request"]["swb_status"] = statuses["swb_status"]

    # Only proceed with workflow if request and reviewer is valid
    if request_valid and reviewer_valid:

        step_fn_client.send_task_success(
            taskToken=arguments["request"]["task_token"], output=json.dumps(arguments)
        )

        logger.info(
            "Request updated successfully and restarting stepfunction workflow..."
        )
        return "Request updated successfully"

    return "Request has not been updated due to invalid input"


# TO-DO: Inject Environment variables for reviewer group names
def determine_status(egress_arguments: Any, reviewer_usergroup: str):
    global egress_status
    global swb_status
    reviewer_list_groups = json.loads(reviewer_list)

    if reviewer_usergroup == reviewer_list_groups[0]:
        inbound_reviewer_1_decision = egress_arguments["request"][
            "ig_reviewer_1_decision"
        ]

        if inbound_reviewer_1_decision == "APPROVED":
            egress_status = "IGAPPROVED"
            swb_status = "PROCESSING"
        else:
            egress_status = "REJECTED"
            swb_status = "PENDING"

    elif reviewer_usergroup == reviewer_list_groups[1]:
        inbound_reviewer_1_decision = egress_arguments["request"][
            "ig_reviewer_1_decision"
        ]
        inbound_reviewer_2_decision = egress_arguments["request"][
            "rit_reviewer_2_decision"
        ]

        if (
            inbound_reviewer_1_decision == "APPROVED"
            and inbound_reviewer_2_decision == "REJECTED"  # noqa W503
        ):
            egress_status = "REJECTED"
            swb_status = "PENDING"
        elif (
            inbound_reviewer_1_decision == "APPROVED"
            and inbound_reviewer_2_decision == "APPROVED"  # noqa W503
        ):
            egress_status = "RITAPPROVED"
            swb_status = "PROCESSED"
        else:
            egress_status = "REJECTED"
            swb_status = "REJECTED"

    else:
        logger.error("Status mapping error with usergroup %s", reviewer_usergroup)
        raise Exception(
            "Unable to determine the status of the request. Please refresh and retry"
        )

    return {"egress_status": egress_status, "swb_status": swb_status}


# Check if egress request is valid and retrieve details from DynanmoDB table
def retrieve_request_details(request_id: str):
    ddb_table = ddb.Table(table)

    response = ddb_table.query(
        KeyConditionExpression=Key("egress_request_id").eq(request_id)
    )
    if not response["Items"] and len(response["Items"]) != 1:
        raise Exception(
            f"No matching egress request found for egress request: {request_id}"
        )
    else:
        return response


# Check if reviewer is valid by matching the current reviewer group field in the DB to the incoming usergroup
def is_reviewer_valid(request_id: str, reviewer_usergroup: str, egress_request: Any):
    current_reviewer_group = egress_request["Items"][0]["current_reviewer_group"]
    if current_reviewer_group == reviewer_usergroup:
        logger.info(
            "Reviewer is in current reviewer group: %s and is valid",
            current_reviewer_group,
        )
        return True
    else:
        logger.error(
            "Egress request: %s found but reviewer is not valid and not found in the current reviewer group: %s",
            request_id,
            current_reviewer_group,
        )
        raise Exception("You are not authorised to update this request at this time")


# Check if SFN task token is valid by matching the task token field in the DB to the incoming task token
def is_request_valid(request_id: str, task_token: str, egress_request: Any):
    if egress_request["Items"][0]["task_token"] == task_token:
        logger.info("Egress request ID and task token is valid")
        return True
    else:
        logger.error(
            "Egress request: %s found but task token %s is not valid",
            request_id,
            task_token,
        )
        raise Exception(
            "Another user may have updated this request. Please refresh to get the latest data"
        )
