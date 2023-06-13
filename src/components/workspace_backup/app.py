#!/usr/bin/env python3

# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks
from src.workspace_backup_infrastructure_stack import WorkspaceBackupInfrastructureStack

app = cdk.App()

WorkspaceBackupInfrastructureStack(app, "WorkspaceBackupInfrastructureStack")
Aspects.of(app).add(AwsSolutionsChecks())

app.synth()
