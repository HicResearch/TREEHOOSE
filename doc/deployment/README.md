# Deployment

---

## Overview

---

The TREEHOOSE TRE uses the **ServiceWorkbench** open-source software as the core component and deploys additional add-ons to enable other features.

1) Ensure all the [prerequisites](./Prerequisites.md) have been added and configured.

2) The deployment of the TREEHOOSE TRE solution will be done from an EC2 instance. Follow the instructions in [Step 1 - Setup Deployment Instance](./Step1-SetupDeploymentInstance.md) to deploy the required resources.

3) Deploy all of the TREEHOOSE TRE solution components in sequential order as specified in the table below:

| Component | Type    | Name                     | Purpose                            | Deployment     |
|:---------:|:--------|:-------------------------|:-----------------------------------|:----------------------------|
| 1         | Core    | [Service Workbench](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/)  | Core engine for TRE. It provides a simple GUI interface for Researchers to provision secure cloud compute resources with data analytics tools. | Follow the instructions in [Step 2 - Deploy ServiceWorkbench](./Step2-DeployServiceWorkbench.md) |
| 2         | Add-on  | [Data Lake](https://aws.amazon.com/lake-formation) | A pre-configured data lake to store and manage sensitive datasets. | Follow the instructions in [Step 3 - Create Data Lake](./Step3-CreateDataLake.md)|
| 3         | Add-on  | Data Egress Application | Provides a GUI-based data egress approval workflow for researchers to take out data from the TRE with the permission of an Information Governance Lead and Research IT | Follow the instructions in [Step 4 - Deploy Data Egress App](./Step4-DeployDataEgressApp.md) |
| 4         | Add-on  | Project Budget Controls | Allows TRE administrators to set policies to stop new ServiceWorkbench workspace creation when the provided budget limit is reached | Follow the instructions in [Step 5 - Add Project Budget Controls](./Step5-AddProjectBudgetControls.md) |
| 5         | Add-on  | Workspace Backup | Allows TRE administrators to backup and restore ServiceWorkbench workspaces | Follow the instructions in [Step 6 - Enable Workspace Backups](./Step6-DeployBackupComponent.md) |

## Tools and Dependencies

---

`TODO information on tools required for installing service workbench. Ex : nvm, npm, pnpx, aws-cdk etc..`

## Source code

---

`TODO information on which Github repos are downloaded in installation process and why`

[Installation Guide](./INSTALLATION.md)

[Uninstallation Guide](./UNINSTALLATION.md)
