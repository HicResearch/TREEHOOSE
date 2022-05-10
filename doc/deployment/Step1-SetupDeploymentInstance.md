# Deployment Instance

Ensure all steps below are executed in AWS region:
 [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

## Step 1. Create Deployment Instance

**Time to deploy**: Approximately 10 minutes

### Step 1A. Create the EC2 instance

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod**
 account and Admin privileges.

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks)
 menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file:
 [deployment instance](../../src/deployment/DeploymentInstance-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TREDeploymentInstance". Adjust default parameter values if needed.
 Press on button *Next* twice and then on button *Create stack*
- [ ] Confirm the stack status is "CREATE_COMPLETE"

### Step 1B. Log in to the EC2 instance

- [ ] Follow these [instructions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/session-manager.html)
 to learn how to connect via SSM to the EC2 instance created in Step 1A.
- [ ] Run the following command to initialise your environment:

```shell
sudo -iu ec2-user
```

### Step 1C. Download TREEHOOSE TRE

- [ ] Run the following commands to get a copy of the TREEHOOSE TRE open-source repository:

```shell
cd /home/ec2-user/tmp
`TODO`
```
