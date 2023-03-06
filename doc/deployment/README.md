# Deployment

The TREEHOOSE TRE solution has only been tested in AWS region [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).
We cannot guarantee the solution or instructions provided will work in other regions and additional work might be required to enable use of other regions.

Please note that most of the deployment instructions will mention the AWS region [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).
However, when accessing certain global AWS services such as [IAM](https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/home),
you will be redirected to another AWS region such as North Virginia (us-east-1).
Please ensure you switch back to the correct region after the redirect.

---

## Overview

---

The TREEHOOSE TRE uses the **ServiceWorkbench** open-source software as the core component and deploys additional add-ons to enable other features.

1) The prerequisites will cover the setup for an AWS Control Tower environment with a multi-account structure.

2) The solution deployment will be done from a pre-configured EC2 instance.

3) The following components are part of the TRE solution:

| Component | Type    | Name                     | Purpose                            |
|:---------:|:--------|:-------------------------|:-----------------------------------|
| 1         | Mandatory | [ServiceWorkbench](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/)  | Core engine for TRE. It provides a simple GUI interface for Researchers to provision secure cloud compute resources with data analytics tools. |
| 2         | Mandatory | [Data Lake](https://aws.amazon.com/lake-formation) | A pre-configured data lake to store and manage sensitive datasets. |
| 3         | Optional  | Data Egress Application | Provides a GUI-based data egress approval workflow for researchers to take out data from the TRE with the permission of an Information Governance Lead and Research IT Admin |
| 4         | Optional  | Project Budget Controls | Allows TRE administrators to set policies to stop new ServiceWorkbench workspace creation when the provided budget limit is reached |
| 5         | Optional  | Workspace Backup | Allows TRE administrators to backup and restore ServiceWorkbench workspaces |

## Tools and Dependencies

---

Some of the required tools with be installed automatically on the EC2 instance deployed in [Step 1 - Setup Deployment Instance](./Step1-SetupDeploymentInstance.md),
while other tools will be installed during the deployment steps.

The main packages used are:

- aws cli
- aws cdk
- git
- python3
- go
- nodejs
- nvm
- pnpm
- serverless
- packer

Please note some of the dependencies like the nvm package will be downloaded from external repositories (e.g. GitHub).
Any package management requirements such as availability and security will need to be covered by the TREEHOOSE solution user.

## Source code

---

| Component |Name                     | Source code location  |
|:---------:|:------------------------|:-----------------------------------|
| 1         | ServiceWorkbench | [Official Open-Source Repository](https://github.com/awslabs/service-workbench-on-aws/releases/tag/v5.2.3) |
| 2         | Data Lake | [CloudFormation Template](../../src/data_lake/DataLake-Cfn.yaml) |
| 3         | Data Egress Application | [CDKv1 Application](./) |
| 4         | Project Budget Controls | [CloudFormation Template](../../src/components/budget_controls/ProjectBudgetControl-Cfn.yaml) |
| 5         | Workspace Backup | [CDKv2 Application](./) |

## [Installation Guide](./INSTALLATION.md)

## [Uninstallation Guide](./UNINSTALLATION.md)
