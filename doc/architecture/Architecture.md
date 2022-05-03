# Architecture

---

## AWS Control Tower

---

## TREEHOOSE (TRE)

---

TREEHOOSE is the Trusted Research Environment (TRE) implementation
that will be deployed for each research project.
Deploying the solution with the **default parameters**
builds the following environment in the AWS Cloud.

![TREEHOOSE Architecture](../../res/images/TREEHOOSE-architecture.png)

### Overview

---

The TREEHOOSE solution is formed of
[Service Workbench on AWS](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/)
and a data lake that together provides the building blocks
for the Trusted Research Environment (TRE) capability.

In addition to the basic building blocks TREEHOOSE solution
provides optional add-on components to enable

- Data egress
- Workspace backups
- Budget controls

### Solution Overview

---

#### *Service Workbench on AWS Solution*

---

Service Workbench on AWS is a cloud solution that enables
IT teams to provide secure, repeatable, and federated control of
access to data, tooling, and compute power that researchers need.
Find more details [here](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/).

#### *Datalake*

---

TREEHOOSE uses a data lake setup that
uses [AWS Lake Formation](https://aws.amazon.com/lake-formation/)
under the hoods for creating a secure and scalable
data store for storing research data.
A data lake is a centralized, curated, and secured repository that stores all your data,
both in its original form and prepared for analysis.
It creates a pre-configured data lake to be used for TRE data pipelines.
This is a mandatory add-on.

#### *Data Egress Application*

---

This add-on provides a data egress approval workflow
for researchers to take out data from TRE with the permission of multiple parties
(data manager, research IT, etc.).
The add-on is hosted as a web application supported by
backend infrastrucutre. Each add-on installation is tied
to a specific TRE project.

The add-on provides a streamlined
process for securely egressing data from the TRE environment
while keeping the TRE admins and Data auditors in complete
control of the process.

All data egress requests and any actions performed on those
are recorded for Audit.

![Egress App Workflow](../../res/images/egress-app-workflow.png)

#### *Workspace backup*

---

This add-on provides capability to periodically
backup researcher workspace to ensure that persistent
data is recoverable in-case researcher workspace is
terminated by mistake.

Once implemented this capability will enable
researchers to select whether they want to enable
periodic workspace backups when creating the workspace.

Only TRE administrators can control the backup frequency
and back retention periods. Also, any restore operations
need to be performed by admins.

This add-on uses [AWS Backup](https://aws.amazon.com/backup/) for backing up block storage attached to
[Amazon EC2](https://aws.amazon.com/ec2/) based compute workspaces while it uses a be-spoke
implementation to backup [Amazon SageMaker Notebook Instances](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html)

Below diagrams explain how the backup solution works
for

1. EC2 based workspaces.
![EC2 backed workspaces](../../res/images/ec2-based-backup-design.png)

1. SageMaker notebook based workspaces
![SageMaker notebook backed workspaces](../../res/images/sagemaker-notebook-backup-design.png)

#### *Budget controls*

---

Budget controls is an optional
add-on that allows administrators and finance stakeholders
of the TRE to stay on top of project finances.
This add-on can optionally be deployed for
each TRE project and allows to

- **Monitor** : set thresholds for sending budget alerts
- **Report** : sending notification on budget usage
- **Repond** : automate actions to avoid over-spending

The add-on uses [AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/)
 to plan and set expectations around TRE project costs.
