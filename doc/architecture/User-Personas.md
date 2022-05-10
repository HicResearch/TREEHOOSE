# User Personas

The TREEHOOSE documentation assumes there are 4 main user roles.
In practice a user may have multiple roles.

## IT Administrators

IT administrators oversee the deployment and configuration of TREEHOOSE, and manage all ongoing technical aspects. Ideally this will be done by a team of people.

Administrators are assumed to have a working knowledge of all governance requirements
for running a trusted research environment, such as knowledge of data protection rules,
how data is managed within the organisation, and how access to use or modify data is governed.
This is outside the scope of the TREEHOOSE documentation.

Advanced knowledge of AWS is not required, but they should be comfortable with managing complex compute infrastructure on-prem or in another cloud.

As a rough guide, administrators should have completed the AWS Cloud Practitioner Essentials course, and ideally the AWS Technical Essentials course. [Both courses are free from AWS](https://aws.amazon.com/training/digital/).
Over time they should seek to develop their knowledge of AWS to support users and implement future customisations of the TREEHOOSE platform.

## Researchers

Researchers use TREEHOOSE to access confidential data that must not be removed from a secure environment.
TREEHOOSE provides researchers with a virtual compute environment with the tools
needed to process data, and generate outputs that can be removed from the TRE following an approval process.

The environment is designed to reduce the possibility of unauthorised removal of
data from the TRE, for example by blocking outbound network traffic.
It is suitable for researchers who want to use standard research tools from their field, but who have no cloud experience.

Researchers with more technical compute experience have the option of accessing
potentially unlimited scaleable compute resources, including AWS services for
handling big data and machine learning, if configured by a TREEHOOSE administrator.

## Data Lake Manager

TREEHOOSE is designed to provide fine-grained control to confidential datasets.
The Data Lake Manager is responsible for uploading datasets to TREEHOOSE, and deciding which users or projects have access to a dataset.
A large part of this role therefore involves governance of the data, and working with data owners to agree on how a dataset can be used.

They may also be responsible for adding new users or disabling old users, for setting up projects, and for controlling which software a user has access to.

## Data Egress Manager

A Data Egress Manager checks all research outputs before they are removed from a TRE, to ensure confidential data is not taken out.
This role requires an understanding the data governance, and may be combined with the Data Lake Manager.

They are expected to understand the types of output that researchers wish to take out of a TRE, and seek advice where outputs are in a format that can not be validated.
