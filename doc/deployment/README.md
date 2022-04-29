# Deployment

The TREEHOOSE TRE solution has only been tested in AWS region [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/). We cannot guarantee the solution or instructions provided will work in other regions and additional work might be required to enable use of other regions.

Please note that most of the deployment instructions will mention the AWS region [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/). However, when accessing certain global AWS services such as [IAM](https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/home), you will be redirected to another AWS region such as North Virginia (us-east-1). Please ensure you switch back to the correct region after the redirect.

---

## Overview

---

The TREEHOOSE TRE uses the **ServiceWorkbench** open-source software as the core component and deploys additional add-ons to enable other features.

1) Ensure all the [prerequisites](./Prerequisites.md) have been added and configured.

2) The solution deployment will be done from an EC2 instance. Follow the instructions in [Step 1 - Setup Deployment Instance](./Step1-SetupDeploymentInstance.md) to deploy the required resources.

3) Deploy all of the TREEHOOSE TRE solution components in sequential order as specified in the table below:

| Component | Type    | Name                     | Purpose                            | Deployment     |
|:---------:|:--------|:-------------------------|:-----------------------------------|:----------------------------|
| 1         | Core    | [ServiceWorkbench](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/)  | Core engine for TRE. It provides a simple GUI interface for Researchers to provision secure cloud compute resources with data analytics tools. | Follow the instructions in [Step 2 - Deploy ServiceWorkbench](./Step2-DeployServiceWorkbench.md) |
| 2         | Add-on  | [Data Lake](https://aws.amazon.com/lake-formation) | A pre-configured data lake to store and manage sensitive datasets. | Follow the instructions in [Step 3 - Create Data Lake](./Step3-CreateDataLake.md)|
| 3         | Add-on  | Data Egress Application | Provides a GUI-based data egress approval workflow for researchers to take out data from the TRE with the permission of an Information Governance Lead and Research IT Admin | Follow the instructions in [Step 4 - Deploy Data Egress App](./Step4-DeployDataEgressApp.md) |
| 4         | Add-on  | Project Budget Controls | Allows TRE administrators to set policies to stop new ServiceWorkbench workspace creation when the provided budget limit is reached | Follow the instructions in [Step 5 - Add Project Budget Controls](./Step5-AddProjectBudgetControls.md) |
| 5         | Add-on  | Workspace Backup | Allows TRE administrators to backup and restore ServiceWorkbench workspaces | Follow the instructions in [Step 6 - Enable Workspace Backups](./Step6-DeployBackupComponent.md) |

## Tools and Dependencies

---

Some of the required tools with be installed automatically on the EC2 instance deployed in [Step 1 - Setup Deployment Instance](./Step1-SetupDeploymentInstance.md), while other tools will be installed during the deployment steps.

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

Please note some of the dependencies like the nvm package will be downloaded from external repositories (e.g. GitHub). Any package management requirements such as availability and security will need to be covered by the TREEHOOSE solution user.

## Source code

---

| Component | Type    | Name                     | Source code location  | 
|:---------:|:--------|:-------------------------|:-----------------------------------|
| 1         | Core    | ServiceWorkbench | [Official Open-Source Repository](https://github.com/awslabs/service-workbench-on-aws/releases/tag/v5.1.1) |
| 2         | Add-on  | Data Lake | [CloudFormation Template](../../src/data_lake/DataLake-Cfn.yaml) |
| 3         | Add-on  | Data Egress Application | [CDKv1 Application](./) |
| 4         | Add-on  | Project Budget Controls | [CloudFormation Template](../../src/components/ProjectBudgetControl-Cfn.yaml) |
| 5         | Add-on  | Workspace Backup | [CDKv2 Application](./) |

[Installation Guide](./INSTALLATION.md)

[Uninstallation Guide](./UNINSTALLATION.md)
