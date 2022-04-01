Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

## Step 1. Create an EC2 Instance

**Time to deploy**: Approximately 10 minutes

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [deployment instance](../../src/deployment/DeploymentInstance-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TREDeploymentInstance". Adjust default parameter values if needed. Press on button *Next* twice and then on button *Create stack*
- [ ] Confirm the stack status is "CREATE_COMPLETE"
