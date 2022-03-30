Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

## Step 1. Create an EC2 Instance

**Time to deploy**: Approximately 10 minutes

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account.

### Step 1A. Create EC2 key pair for SSH access

- [ ] Go to Service: [Amazon EC2](https://eu-west-2.console.aws.amazon.com/ec2/v2/home?region=eu-west-2)
- [ ] Follow these [instructions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair) to create a key

### Step 1B. Obtain IP address

The EC2 instance used for deploying the solution is protected by a security group restricting network access to it.

Before you can create the instance in step 1C, you will need the IP address of the machine from which you will initiate the SSH connection to the EC2 instance.

To view your IP address, you can use this link: https://checkip.amazonaws.com/.

### Step 1C. Launch pre-configured EC2 instance

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [deployment instance](./) and press on button *Next*
- [ ] Provide *Stack name*: "TREDeploymentInstance", *InstanceAllowIP*: the IP found in step 1B and *InstanceKeyName*: select key created in step 1A. Press on button *Next* twice and then on button *Create stack*
- [ ] Confirm the stack status is "CREATE_COMPLETE"
