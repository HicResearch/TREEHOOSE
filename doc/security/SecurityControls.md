# Security Controls

To learn about AWS general security best practices, please review the [Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/security.html) of the AWS Well-Architected Framework.

## Shared Responsibility Model

The TREEHOOSE TRE solution runs on the AWS cloud where security and compliance is a shared responsibility between AWS and the customer.

To learn more about the shared responsibility model, please review the [official guidance](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/shared-responsibility.html).

## Data Classification

Data classification is determined by a number of participants, including, but not limited to, 3rd party dataset providers and principal investigators who lead research projects. Classification is not a property of a dataset, because a dataset’s sensitivity also depends on the data it can be combined with and its use.

- Under-classification can lead to legal and financial sanction and the loss of the social license to operate in the research community.
- Over-classification can result in lost researcher productivity, a loss of scientific engagement and increases data risk by encouraging workaround breach.

The TREEHOOSE TRE solution is designed to be flexible and does not enforce any tagging mechanism or workflows specific to data classification tiers. It is the responsability of the TRE administrator and the Data managers to configure the TRE environment and datasets to meet their data classification requirements.

## Data Ingress

The datasets used in research activities are stored in a data lake provided as part of the TREEHOOSE TRE solution with encryption applied by default at rest and in transit. The TRE administrator can configure custom access and security policies to manage the data lake in a secure manner.

Researchers can only be provided with read-only access to a dataset. If a dataset contains sensitive information or needs changes, a Data Manager will need to process the data in the data lake before allowing access to it for research activities.

## Data Egress

Researchers can extract data from the TRE environment only by undergoing a 2-stage approval process involving Information Governance Leads and Research IT Admins. An add-on application enables a secure data egress workflow that will move the encrypted data securely out of a workspace and into the data lake provided as part of the TREEHOOSE TRE solution.

After all the approvals are given, Information Governance Leads will be able to download the egressed data for a maximum number of times as set by the TRE administrator.

## Software Ingress

The compute workspaces used by researchers are network-isolated and do not have Internet access. The TRE administrator needs to configure a suitable workspace type or attach a storage location with the required packages before any workspaces are created.

## User Access Management

The 2 web applications part of the TREEHOOSE TRE solution use Amazon Cognito as an identity provider and have a set of predefined roles that are assigned to users by a TRE administrator. Some permissions can also be assigned to control user access to compute workspaces and datasets.

## User Device Management

All resources part of the TREEHOOSE TRE solution are stored on the AWS cloud. Users will need an Internet or dedicated network connection to access the TRE-related web applications and resources, the web-based virtual remote desktop application or the AWS web console for administration purposes.
