# Configuration Guide

Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

**Total time to configure**: Approximately 30 minutes

To use the Egress Application add-on after deployment, a TRE admin must additionally configure user accounts
and enable the information governance leads to review the data in the egress requests triggered by researchers.

There are 2 types of users involved in the Egress App workflow:

1. Information Governance Leads

- uses a SWB user account of type researcher to create a new workspace to view the contents of the data egress request
- uses an Egress App user account to provide the 1st approval for a data egress request

1. Research IT Admins

- uses a SWB user account of type admin to validate that an information governance lead is authorised to grant their approval
- uses an Egress App user account to provide the 2nd approval for data egress requests, only after the 1st approval has been granted

## Step 1. Setup Users

**Time to configure**: Approximately 15 minutes

Apply these steps only to accounts that are part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod**
account and Admin privileges.

### Part 1. SWB

Create Cognito users who can authenticate to the SWB website

In Cognito:

- [ ] Go to Service: [AWS Cognito](https://eu-west-2.console.aws.amazon.com/cognito/home?region=eu-west-2)
- [ ] Select [_Manage User Pools_](https://eu-west-2.console.aws.amazon.com/cognito/users/?region=eu-west-2)
- [ ] Select the _User Pool_ for SWB called e.g. _treprod-pj1-userPool_ (based on the SWB config file provided
      during [deployment Step 2C](../../deployment/Step2-DeployServiceWorkbench.md))
- [ ] Under _General settings_, select menu option _Users and groups_
- [ ] Use button _Create user_ to create at least one SWB user to represent an Information Governance Lead
- [ ] Use button _Create user_ to create at least one SWB user to represent a Research IT Admin

In SWB:

- [ ] Log in to SWB using the root account (based on the SWB config file provided during
      [deployment Step 2C](../../deployment/Step2-DeployServiceWorkbench.md))
- [ ] Go to menu option _Users_
- [ ] For each user previously created in Cognito use buttons _Detail_ -> _Activate User_ to activate them to allow login
- [ ] For each user of type Information Governance Lead previously created in Cognito use buttons _Detail_ -> _Edit_
      to select _User Role_: researcher
- [ ] For each user of type Research IT Admin previously created in Cognito use buttons _Detail_ -> _Edit_ to select _User Role_: admin

### Part 2. Egress App

Create Cognito users who can authenticate to the Egress App website

- [ ] Go to Service: [AWS Cognito](https://eu-west-2.console.aws.amazon.com/cognito/home?region=eu-west-2)
- [ ] Select [_Manage User Pools_](https://eu-west-2.console.aws.amazon.com/cognito/users/?region=eu-west-2)
- [ ] Select the _User Pool_ for the Egress App called e.g. \*EgressUserPool\*\*
- [ ] Under _General settings_, select menu option _Users and groups_. View tab _Groups_, you should see the 2 types
      of reviewers: InformationGovernance and TREAdmin
- [ ] Select tab _Users_
- [ ] Use button _Create user_ to create at least one user of type Information Governance Lead. After creating the user,
      select it and use button _Add to group_ to add it to the InformationGovernance group
- [ ] Use button _Create user_ to create at least one user of type Research IT Admin. After creating the user, select
      it and use button _Add to group_ to add it to the TREAdmin group

### Part 3. Notifications

Ensure Egress App users receive notifications when egress requests are triggered.

- [ ] Go to Service: [Amazon SNS](https://eu-west-2.console.aws.amazon.com/sns/v3/home?region=eu-west-2#/homepage)
- [ ] Select [_Topics_](https://eu-west-2.console.aws.amazon.com/sns/v3/home?region=eu-west-2#/topics)

Select topic _Information-Governance-Notifications_:

- [ ] For each user of type Information Governance Lead created in Part 2, use button _Create subscription_ and
      select _Protocol_: Email. In _Endpoint_ provide the user's email address. Submit and the user will receive an email to confirm the subscription

Select topic _ResearchIT-Notifications_:

- [ ] For each user of type Research IT Admin created in Part 2, use button _Create subscription_ and select
      _Protocol_: Email. In _Endpoint_ provide the user's email address. Submit and the user will receive an email to confirm the subscription

If you are able to create your own email groups (e.g. Outlook groups) that can receive external emails you can create a subscription for the group email address instead, and manage subscriptions outside of AWS.

## Step 2. Setup Access for Information Governance Leads

**Time to configure**: Approximately 15 minutes

Before proceeding with the steps below, please be aware of the following limitations in SWB:

- The _Admin_ permissions for a registered data study should always have at least one SWB user
  (of type Information Governance Lead) listed
- Do not add the same SWB user under both _Admin_ and _Read Only_ permissions for a registered data study as
  it leads to permission errors when viewing the study
- Once an external S3 bucket is registered as data study, it cannot be updated nor deleted. Please view the
  [troubleshooting guide](../../troubleshooting/TroubleshootingRunbook.md#external-data-studies) for instructions
  on how to handle this situation

Follow the instructions below to provide SWB users of type Information Governance Lead with access to view
the egress requests made by researchers in SWB.

In SWB:

- [ ] Log in to SWB using an admin account
- [ ] Select menu option _Data Sources_ and use button _Register Studies_, press _Next_
- [ ] Provide the following details:

| Parameter Name            | Description                                                                                                                                                                                                                                                                                                     |
| :------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS Account ID            | Provide the ID for the **TRE Project 1 Prod** account                                                                                                                                                                                                                                                           |
| Account Name              | Provide e.g. **TRE Project 1 Prod**                                                                                                                                                                                                                                                                             |
| Region                    | Provide the AWS Region where the TRE project was deployed, e.g. _eu-west-2_ for London                                                                                                                                                                                                                          |
| Bucket Name               | Provide the name of the S3 bucket created by the Egress App as staging area for egress requests, e.g. EgressStagingArea... ; Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) _Resources_ tab for _Stack_ "EgressAppBackend" to locate the S3 bucket |
| Bucket Region             | Provide the AWS Region where the TRE project was deployed, e.g. _eu-west-2_ for London                                                                                                                                                                                                                          |
| Bucket Default Encryption | Select _SSE-KMS_ and provide the KMS Arn used for the Egress App staging area S3 Bucket's encryption key, e.g. EgressS3Key...; Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) _Resources_ tab for _Stack_ "EgressAppBackend" to locate the KMS key |

- [ ] Press on button "Add Study":

| Parameter Name        | Description                                                                                                                                                                                                                                                                                |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Study Id & Study Name | Provide a name for the directory that will be mounted to a workspace, e.g. EgressRequests                                                                                                                                                                                                  |
| Study Folder          | Provide just the forward slash character _/_ . This will allow the Information Governance Lead to view all of the TRE project's egress requests for all workspaces                                                                                                                         |
| Project               | Provide the associated SWB project e.g. _TREProject1Prod_                                                                                                                                                                                                                                  |
| Type                  | Select _Organization Study_                                                                                                                                                                                                                                                                |
| Access                | Select _Read Only_                                                                                                                                                                                                                                                                         |
| Study KMS Arn         | Provide the KMS Arn used for the Egress App staging area S3 Bucket's encryption key, e.g. EgressS3Key...; Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) _Resources_ tab for _Stack_ "EgressAppBackend" to locate the KMS key |
| Admin                 | Select an existing SWB user account for the Information Governance Lead, as created in Step 1 - Part 1                                                                                                                                                                                     |

A message like this should appear after registering the study:

![Successfully registered the staging area for egress requests](../../../res/images/Status-RegisterStudy-EgressRequests.png)

A message like this should appear after successfully attaching the study:

![Successfully attached the staging area for egress requests](../../../res/images/Status-SetupDataStudy-EgressRequests.png)

To view data egress requests, a SWB user of type Information Governance Lead needs to launch a SWB Workspace
with this Study attached to it.
