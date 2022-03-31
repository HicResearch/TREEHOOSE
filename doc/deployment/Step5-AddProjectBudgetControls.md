Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

## Step 5. Add Project Budget Controls

**Time to deploy**: Approximately 10 minutes

Due to design considerations, do this step once for any account part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account.

### Step 5A. Find existing IAM role

- [ ] Go to Service: [AWS Identity and Access Management](https://us-east-1.console.aws.amazon.com/iamv2/home#/home)
- [ ] Select the [*Roles*](https://us-east-1.console.aws.amazon.com/iamv2/home#/roles) menu option on the left side
- [ ] Search for *initial-stack*
- [ ] Extract number ID from role: *initial-stack-<number_ID>-xacc-env-mgmt*. This number is required in Step 5B

### Step 5B. Add Project Budget Control

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [project budget controls](../../src/components/ProjectBudgetControl-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TREProject1ProdBudgetControl". Add the parameters required. Press on button *Next* twice and then press on button *Create stack*

|Parameter Name|Description|Default value|
|:-----------------|:-----------|:-------------|
|AnnualBudgetLimit|Estimated annual account spend in USD|*No default - must be specified*|
|AnnualBudgetNotificationThreshold1|Budget threshold percentage for receiving first notification|*80*|
|AnnualBudgetNotificationThreshold2|Budget threshold percentage for receiving second notification|*99*|
|AnnualBudgetActionThreshold|Budget threshold percentage for stopping new SWB workspace creation|*99*|
|BudgetNotifySNSTopicName|The name of the SNS topic whose subscribers (includes TREAdminEmailAddress) receive alerts regarding project budget|*No default - must be specified*|
|TREAdminEmailAddress|The email address for the TRE admin who will receive alerts regarding project budget|*No default - must be specified*|
|SWBStackID|Specify the ID of existing IAM role initial-stack-<ID>-xacc-env-mgmt|*No default - must be specified*|

- [ ] Confirm the stack status is "CREATE_COMPLETE"

### Step 5C. Adjust Project Budget

This step is optional if you need to update the project budget settings.

- [ ] Go to Service: [AWS Budgets](https://us-east-1.console.aws.amazon.com/billing/home?region=us-east-1&skipRegion=true#/budgets/overview)
- [ ] Select the budget created in Step 5B and edit as needed
- [ ] View how to manage your costs with AWS Budgets on this [page](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
