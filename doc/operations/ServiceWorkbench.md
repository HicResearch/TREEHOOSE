# ServiceWorkbench

[Service Workbench on AWS](https://aws.amazon.com/government-education/research-and-technical-computing/service-workbench/)
 is a cloud solution that enables IT teams to provide secure, repeatable, and federated control of access to data, tooling,
 and compute power that researchers need.

## Design Constraints

As described in the [TREEHOOSE TRE architecture](../architecture/Architecture.md), one TRE Project account will host only
 one SWB instance.

For a SWB instance (web application), a TRE admin should **create only one SWB Project** which will represent the TRE project
 whose boundaries are defined by the AWS account (e.g. **TRE Project 1 Prod**) where all project related resources are deployed.

## Create the SWB Project

To create the SWB project required to perform any tasks in SWB (create workspaces, register data studies, etc.), follow the
 [instructions](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 from the official SWB user guide, pages 17-18.

## Create SWB Users

### Roles

To learn about the predefined user roles available in SWB, follow the
 [guidance](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 from the official SWB user guide, page 16.

### Users

To create new SWB users, follow the instructions below to create Cognito users who can authenticate to the SWB website.

Apply these steps only to accounts that are part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod**
 account and Admin privileges.

In Cognito (default IdP):

- [ ] Go to Service: [AWS Cognito](https://eu-west-2.console.aws.amazon.com/cognito/home?region=eu-west-2)
- [ ] Select [*Manage User Pools*](https://eu-west-2.console.aws.amazon.com/cognito/users/?region=eu-west-2)
- [ ] Select the *User Pool* for SWB called e.g. *treprod-pj1-userPool* (based on the SWB config file provided during
 [deployment Step 2C](../../deployment/Step2-DeployServiceWorkbench.md))
- [ ] Use button *Create user* to create a SWB user

In SWB:

- [ ] Log in to SWB using the root account (based on the SWB config file provided during
 [deployment Step 2C](../../deployment/Step2-DeployServiceWorkbench.md))
- [ ] Go to menu option *Users*
- [ ] For each user previously created in Cognito use buttons *Detail* -> *Activate User* to activate them to allow login
- [ ] For each user previously created in Cognito use buttons *Detail* -> *Edit* to select a suitable *User Role* for them

### Add Users to Project

To add users to the SWB project, follow the
 [instructions](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 from the official SWB user guide, page 18 - section *Adding a User to a Project*.

## Register Data Studies

An admin in SWB needs to register a data study and assign permissions to that data study. Afterwards, a researcher can
 attach that read-only data study to a compute workspace to perform their research activities.

To learn how to register external data studies, follow the
 [instructions](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 from the official SWB user guide, pages 26-28.

To learn how to set permissions to data studies, follow the
 [instructions](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 from the official SWB user guide, page 25.

For known issues with registered data studies in SWB, please refer to the
 [troubleshooting guidance](../troubleshooting/TroubleshootingRunbook.md), section *External Data Studies*.

## Create Workspaces

An admin in SWB needs to define workspace types and configurations before a researcher can use those configurations to
 create compute workspaces to perform research activities.

To learn about operating workspaces, follow the
 [instructions](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 from the official SWB user guide, pages 11-14.

## Learn More

For more SWB guidance, please consult the
 [official SWB user guide](https://github.com/awslabs/service-workbench-on-aws/blob/v5.1.1/docs/Service_Workbench_User_Guide.pdf)
 or ask questions in the [project's Issues page on GitHub](https://github.com/awslabs/service-workbench-on-aws/issues).
