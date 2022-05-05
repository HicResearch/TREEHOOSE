# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

from aws_lambda_powertools import Logger, Metrics, Tracer
from download_data import download_data
from list_requests import list_requests
from update_request import update_request

tracer = Tracer(service="EgressApiLambda")
logger = Logger(service="EgressApiLambda")
metrics = Metrics(service="EgressApiLambda", namespace="EgressRequests")


@metrics.log_metrics()
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, context):

    field = event['field']
    usergroup = event['usergroup'][0]

    arguments = event['arguments'] if 'arguments' in event else False
    logger.debug("Invoking API: " + field)

    if field == 'listRequests':
        return list_requests()

    elif field == 'updateRequest':
        if arguments:
            arguments['request']['usergroup'] = usergroup
            return update_request(arguments, context)
        else:
            response = "Arguments not supplied"
            logger.error(response)

    elif field == 'downloadData':
        if arguments:
            return download_data(arguments, context)
        else:
            response = "Arguments not supplied"
            logger.error(response)

    else:
        response = "Unexpected API request type"
        logger.error(response)

    return response
