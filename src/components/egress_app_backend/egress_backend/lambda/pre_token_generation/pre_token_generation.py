# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
import os

from aws_lambda_powertools import Logger

logger = Logger(service="PreTokenGeneration", sample_rate=0.1)

reviewer_list = os.environ['REVIEWER_LIST']


def custom_groups_exist(event: str):
    """
    Utility method to determine if the passed in event contains the custom groups attribute.
    """
    return event['request']['userAttributes'].get('custom:groups') is not None


@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    """
    This function handles adding a custom group to the cognito ID token. This will only be done
    if the user has logged in via an IdP. Otherwise, if the user has logged in via Cognito directly
    then any Cognito groups that they are assigned to will already be mapped to the cognito:groups
    attribute.

    :param event: Cognito ID token passed in as an event
    :type string

    :return bool
    """
    # If custom group attribute exists, modify the token. Otherwise return as is
    if custom_groups_exist(event):
        # Get the custom:groups attribute
        adfs_groups = event['request']['userAttributes']['custom:groups']
        user_id = event['request']['userAttributes']['sub']
        reviewer_list_groups = json.loads(reviewer_list)

        # Loop through expected groups and check for a match
        for group in reviewer_list_groups:
            if group in adfs_groups:
                # override claim in ID token
                logger.debug("Performing group override after matching custom group: %s for user with sub: %s", str(group), str(user_id))
                event["response"]["claimsOverrideDetails"] = {
                    "groupOverrideDetails": {
                        "groupsToOverride": [group]
                    }
                }

    # return ID token to Amazon Cognito
    return event
