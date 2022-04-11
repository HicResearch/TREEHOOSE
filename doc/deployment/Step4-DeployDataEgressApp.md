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

#### Part 1. Create initial resources

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [setup initial resources](../../src/secure_data_egress/SetupInitialResources-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TRESecureEgressAppResources". Press on button *Next* twice and then press on button *Create stack*

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

- [ ] Run the following commands to download the source code:
```
mkdir ~/egress-addon
cd ~/egress-addon
aws s3 cp s3://<bucket from Step 4A>/secure-egress-backend secure-egress-backend --recursive
aws s3 cp s3://<bucket from Step 4A>/secure-egress-webapp secure-egress-webapp --recursive
```

### Step 4C. Deploy backend infrastructure

- [ ] Run the following commands to edit the parameters for the CDK backend stack:
```
... modify cdk.json file (note egress app URL is created in Step 4A)
```

- [ ] Run the following commands to create an isolated Python environment and deploy the CDK backend stack:
```
cd ~/egress-addon/secure-egress-backend
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
npm install -g aws-cdk@1.144.0
cdk deploy
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

- [ ] Run the following commands to copy the packaged React frontend to S3:
```
cd ~/egress-addon/secure-egress-webapp/build
zip -r ../build.zip ./
cd ..
aws s3 cp build.zip s3://<bucket from Step 4A>
```

- [ ] Run the following commands to host the React frontend code in the Amplify app created in Step 4A:
```
aws amplify start-deployment --app-id <app_id from Step 4A> --branch-name <branch_name from Step 4A> --source-url "s3://<bucket from Step 4A>/build.zip"
```
