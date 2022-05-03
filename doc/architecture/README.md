# Architecture

---

Deploying this solution with the **default parameters**
builds the following environment in the AWS Cloud.

![TREEHOOSE Architecture](../../res/images/TREEHOOSE-architecture.png)

## Overview

---

The TREEHOOSE solution uses
[Service Workbench on AWS](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/) as the core engine
for the Trusted Research Environment (TRE) capability.

## Solution Overview

---

### *Service Workbench on AWS Solution*

Service Workbench on AWS is a cloud solution that enables
IT teams to provide secure, repeatable, and federated control of
access to data, tooling, and compute power that researchers need.
Find more details [here](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/).

### *Datalake*

TREEHOOSE uses a data lake setup that
uses [AWS Lake Formation](https://aws.amazon.com/lake-formation/)
under the hoods for creating a secure and scalable
data store for storing research data.
A data lake is a centralized, curated, and secured repository that stores all your data, both in its original form and prepared for analysis.
This is an optional add-on that you can use for
managing research data.

### *Data Egress Application*

This add-on provides a data egress approval workflow
for researchers to take out data from TRE with the permission of multiple parties
(data manager, research IT, etc.).
The add-on is hosted as a web application and tied
to a specific TRE project. It provides a streamlined
process for securely egressing from the TRE environment
while keeping the TRE admins and Data auditors complete
control of the process.

### *Centralised Logging*

The TREEHOOSE implementation is built to help
manage TRE projects at scale. As the number of
TRE projects scale it becomes difficult to manage
the logs at scale. Centralized logging provides a
single point of access to all salient logs generated
across accounts and regions, and is critical for
auditing, security and compliance.

This optional add-on based on the princples
outlined in
[this](https://aws.amazon.com/blogs/architecture/stream-amazon-cloudwatch-logs-to-a-centralized-account-for-audit-and-analysis/)
blog post and
[this](https://github.com/CloudSnorkel/CloudWatch2S3) opensource
solution helps to centralise the logging
from all TRE environments.

The solution aligns with centralised logging setup
by AWS Control Tower and reuses the Log Archive
account created under the Security Organisational Unit.
The key aspect of this add-on to aggregate the application
logs from all TRE projects to a central S3 bucket.

### *Workspace backup*

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

### *Budget controls*

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

## Design considerations

---

## User personas

---

## Cost

---
