#!/usr/bin/env python3

# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

from aws_cdk import core as cdk
from aws_cdk.core import Aspects, Tags
from cdk_nag import AwsSolutionsChecks
from egress_backend_stack import EgressBackendStack

ENVIRONMENT_TYPE = "Prod"

app = cdk.App()

egress_backend_stack = EgressBackendStack(
    app, "EgressAppBackend", env_id=ENVIRONMENT_TYPE
)

Tags.of(egress_backend_stack).add("Environment", ENVIRONMENT_TYPE)
for tag_key, tag_value in app.node.try_get_context(ENVIRONMENT_TYPE)[
    "resource_tags"
].items():
    Tags.of(egress_backend_stack).add(tag_key, tag_value)

# Stack security scanning
Aspects.of(app).add(AwsSolutionsChecks())

app.synth()
