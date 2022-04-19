Syl's Note: I'd like a SA to validate this is the expected configuration

Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

To use the secure egress application add-on after deployment, a TRE admin must additionally configure user accounts and enable the information governance leads to review the data in the egress requests triggered by researchers.

There are 2 types of users involved in the egress app workflow:
1) Information Governance Leads
- uses a SWB user account of type researcher to create a new workspace to view the contents of the data egress request
- uses an egress app user account to provide the 1st approval for a data egress request
2) Research IT Admins
- uses a SWB user account of type admin to validate that an information governance lead is authorised to grant their approval
- uses an egress app user account to provide the 2nd approval for data egress requests, only after the 1st approval has been granted

## Step 1. Setup Users

**Time to configure**: Approximately 15 minutes

Apply these steps only to accounts part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.

### Part 1. SWB

Create Cognito users who can authenticate to the SWB website

In Cognito:
- [ ] Go to Service: [AWS Cognito](https://eu-west-2.console.aws.amazon.com/cognito/home?region=eu-west-2)
- [ ] Select [*Manage User Pools*](https://eu-west-2.console.aws.amazon.com/cognito/users/?region=eu-west-2)
- [ ] Select the *User Pool* for SWB called e.g. *treprod-pj1-userPool* (based on the SWB config file provided during deployment)
- [ ] Under *General settings*, select menu option *Users and groups*
- [ ] Use button *Create user* to create at least one SWB user to represent an Information Governance Lead
- [ ] Use button *Create user* to create at least one SWB user to represent a Research IT Admin

In SWB:
- [ ] Log in to SWB using the root account (based on the SWB config file provided during deployment)
- [ ] Go to menu option *Users*
- [ ] For each user previously created in Cognito use buttons *Detail* -> *Activate User* to activate them to allow login
- [ ] For each user of type Information Governance Lead previously created in Cognito use buttons *Detail* -> *Edit* to select *User Role*: researcher
- [ ] For each user of type Research IT Admin previously created in Cognito use buttons *Detail* -> *Edit* to select *User Role*: admin

### Part 2. Egress App

Create Cognito users who can authenticate to the Egress App website

- [ ] Go to Service: [AWS Cognito](https://eu-west-2.console.aws.amazon.com/cognito/home?region=eu-west-2)
- [ ] Select [*Manage User Pools*](https://eu-west-2.console.aws.amazon.com/cognito/users/?region=eu-west-2)
- [ ] Select the *User Pool* for the Egress App called e.g. *EgressUserPool<string>*
- [ ] Under *General settings*, select menu option *Users and groups*. View tab *Groups*, you should see the 2 types of reviewers: InformationGovernance and TREAdmin
- [ ] Select tab *Users*
- [ ] Use button *Create user* to create at least one user of type Information Governance Lead. After creating the user, select it and use button *Add to group* to add it to the InformationGovernance group
- [ ] Use button *Create user* to create at least one user of type Research IT Admin. After creating the user, select it and use button *Add to group* to add it to the TREAdmin group

### Part 3. Notifications

Ensure Egress App users receive notifications when egress requests are triggered.

- [ ] Go to Service: [Amazon SNS](https://eu-west-2.console.aws.amazon.com/sns/v3/home?region=eu-west-2#/homepage)
- [ ] Select [*Topics*](https://eu-west-2.console.aws.amazon.com/sns/v3/home?region=eu-west-2#/topics)

Select topic *Information-Governance-Notifications*:
- [ ] For each user of type Information Governance Lead created in Part 2, use button *Create subscription* and select *Protocol*: Email. In *Endpoint* provide the email address of the user

Select topic *ResearchIT-Notifications*:
- [ ] For each user of type Research IT Admin created in Part 2, use button *Create subscription* and select *Protocol*: Email. In *Endpoint* provide the email address of the user

## Step 2. Setup Access for Information Governance Leads

To Do