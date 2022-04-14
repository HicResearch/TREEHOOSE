Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

If this add-on application is added, a researcher can use a GUI-based data egress approval workflow to take out data from the TRE with the permission of multiple parties (Information Governance Lead, Research IT).

## Prerequisites

Apply these prerequisites only to accounts part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.

### Remove email restrictions

By default, a new AWS account will be placed in the [Amazon SES](https://aws.amazon.com/ses/) sandbox which enforces a set of restrictions.

To enable the app to send emails to the relevant already-approved parties (information governance leads, IT admins and researchers), an admin must also manually add each email as a verified entity in SES. Following that, the person with the email address must then confirm the registration using a link received in an email.

To skip the need to manually add and verify each email address in Amazon SES, you should request production access to SES by following these [instructions](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html).

## Step 4. Deploy Data Egress App

**Time to deploy**: Approximately ? minutes

Apply these steps only to accounts part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.

### Step 4A. Setup resources before deployment

This step can be removed when we can download the code from the public repository later.

#### Part 1. Create temporary resources

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [setup initial resources](../../src/secure_data_egress/ToBeRemoved-SetupTemporaryResources-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TRESecureEgressAppTempResources". Press on button *Next* twice and then press on button *Create stack*

#### Part 2. Upload source code to S3 bucket

- [ ] Go to Service: [Amazon S3](https://console.aws.amazon.com/s3/get-started?region=eu-west-2)
- [ ] Select the [*Buckets*](https://console.aws.amazon.com/s3/buckets?region=eu-west-2) menu option on the left side
- [ ] Select the S3 bucket created in Part 1 (check CloudFormation stack Outputs for resource names)
- [ ] Upload each of the 2 folders (**secure-egress-backend** and **secure-egress-webapp** from `TO ADD`) using button "Add folder".

### Step 4B. Log in to the EC2 instance

- [ ] Follow these [instructions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/session-manager.html) to learn how to connect via SSM to the EC2 instance created in Step 1.
- [ ] Run the following commands to initialise your environment:
```
sudo su ec2-user
source ~/.bash_profile
```

- [ ] Run the following commands to download the source code (temporarily using S3):
```
mkdir ~/egress-addon
cd ~/egress-addon
aws s3 cp s3://<bucket from Step 4A>/secure-egress-backend secure-egress-backend --recursive
aws s3 cp s3://<bucket from Step 4A>/secure-egress-webapp secure-egress-webapp --recursive
```

### Step 4C. Deploy backend infrastructure

- [ ] Edit file *cdk.json* in the **secure-egress-backend** directory. Change the following required parameters for the CDK backend stack:

|Parameter Name|Description|Location|AWS Account|
|:-----------------|:-----------|:-------------|:------------|
|egress_app_id|Provide resource created in Prerequisites Step 5 - Amplify app ID (not the full Arn, just the ID) |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "Prerequisite-AmplifyApp" or go to [AWS Amplify](https://eu-west-2.console.aws.amazon.com/amplify/home?region=eu-west-2#/home)| **TRE Project 1 Prod** account |
|egress_app_branch|Provide resource created in Prerequisites Step 5 - Amplify app branch name (not the full Arn, just the branch name given as input parameter) |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "Prerequisite-AmplifyApp" or go to [AWS Amplify](https://eu-west-2.console.aws.amazon.com/amplify/home?region=eu-west-2#/home)| **TRE Project 1 Prod** account |
|egress_app_url|Provide resource created in Prerequisites Step 5 - Amplify app URL, e.g. "https://<branch_name>.<app_id>.amplifyapp.com |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "Prerequisite-AmplifyApp" or go to [AWS Amplify](https://eu-west-2.console.aws.amazon.com/amplify/home?region=eu-west-2#/home)| **TRE Project 1 Prod** account |
|swb_egress_store_arn|Provide resource created in Step 2 - S3 Bucket: Egress Store Bucket Arn |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "treprod-ldn-pj1-backend" or go to [Amazon S3 Buckets](https://s3.console.aws.amazon.com/s3/buckets?region=eu-west-2)| **TRE Project 1 Prod** account |
|swb_egress_notification_topic|Provide resource created in Step 2 - SNS Topic: Egress Notification Topic |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "treprod-ldn-pj1-backend" or go to [Amazon SNS Topics](https://eu-west-2.console.aws.amazon.com/sns/v3/home?region=eu-west-2#/topics)| **TRE Project 1 Prod** account |
|swb_egress_notification_bucket_arn|Provide resource created in Step 2 - S3 Bucket: Egress Notification Bucket Arn |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "treprod-ldn-pj1-backend" or go to [Amazon S3 Buckets](https://s3.console.aws.amazon.com/s3/buckets?region=eu-west-2)| **TRE Project 1 Prod** account |
|swb_egress_notification_bucket_kms_arn|Provide resource created in Step 2 - KMS Key: Egress Store Encryption Key Arn |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "treprod-ldn-pj1-backend" or go to [AWS KMS Keys](https://eu-west-2.console.aws.amazon.com/kms/home?region=eu-west-2#/kms/keys)| **TRE Project 1 Prod** account |
|swb_egress_store_db_table|Provide resource created in Step 2 - DynamoDB Table: Egress Store Table Arn |Check [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/) *Resources* tab for *Stack* "treprod-ldn-pj1-backend" or go to [Amazon DynamoDB Tables](https://eu-west-2.console.aws.amazon.com/dynamodbv2/home?region=eu-west-2#tables)| **TRE Project 1 Prod** account |
|datalake_target_bucket_arn|Provide resource created in Step 3|To Do| **TRE Datalake 1 Prod** account |
|datalake_target_bucket_kms_arn|Provide resource created in Step 3|To Do| **TRE Datalake 1 Prod** account |
|cognito_userpool_domain|Provide name for a new Amazon Cognito domain to be created|NA| **TRE Project 1 Prod** account |
|tre_admin_email_address|Provide a TRE admin email address that will need to be verified after deployment|NA| **TRE Project 1 Prod** account |

- [ ] Run the following commands to create an isolated Python environment and deploy the CDK backend stack:
```
cd ~/egress-addon/secure-egress-backend
alias cdkv1="npx aws-cdk@1.144"
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
cdkv1 deploy
```

### Step 4D. Deploy web app

- [ ] Run the following commands to edit the environment variables to point to the deployed backend resources:
```
... modify .env.local file (based on resources created in Step 4C)
```

- [ ] Run the following commands to build the React frontend code:
```
cd ~/egress-addon/secure-egress-webapp
npm install
npm audit fix
npm run build
```

- [ ] Run the following commands to copy the packaged React app to S3 and trigger an automatic deployment to Amplify:
```
cd ~/egress-addon/secure-egress-webapp/build
zip -r ../build.zip ./
cd ~/egress-addon/secure-egress-webapp
aws s3 cp build.zip s3://<bucket from Step 4C>
```

Verify the Amplify app has been updated automatically and the website is reachable:
- [ ] Go to Service: [AWS Amplify](https://eu-west-2.console.aws.amazon.com/amplify/home?region=eu-west-2#/)
- [ ] Select the app and branch created in Step 4A
- [ ] Confirm the status in the app branch is: *Deployment successfully completed.*
- [ ] Open the URL from *Domain* and confirm a login prompt appears like in the image below

![Egress App Website](../../res/images/Status-EgressAppDeployed.png)
