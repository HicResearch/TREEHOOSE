#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks

from src.workspace_backup_infrastructure_stack import WorkspaceBackupInfrastructureStack

app = cdk.App()

WorkspaceBackupInfrastructureStack(app, "WorkspaceBackupInfrastructureStack")
Aspects.of(app).add(AwsSolutionsChecks())

app.synth()
