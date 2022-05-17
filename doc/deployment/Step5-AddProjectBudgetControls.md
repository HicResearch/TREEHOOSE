# Budget Controls Deployment

Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

If this component is added, a TRE project will automatically set policies to stop new SWB workspace creation when the provided budget limit is reached.

## Step 5. Add Project Budget Controls

**Time to deploy**: Approximately 10 minutes

Apply these steps only to accounts part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.

### Step 5A. Locate existing IAM role

- [ ] Go to Service: [AWS Identity and Access Management](https://us-east-1.console.aws.amazon.com/iamv2/home#/home)
- [ ] Select the [*Roles*](https://us-east-1.console.aws.amazon.com/iamv2/home#/roles) menu option on the left side
- [ ] Search for *initial-stack*
- [ ] Extract number ID from role: *initial-stack-{number_ID}-xacc-env-mgmt*. This number is required in Step 5C

### Step 5B - Optional. Locate default SWB Workspace Types

SWB workspace types are represented by Service Catalog products.

The default behaviour is to restrict all SWB workspace types when the budget control policy is applied.
To restrict workspace creation for just the 4 default workspace types SWB creates, follow the instructions below.

- [ ] Go to Service: [AWS Service Catalog](https://eu-west-2.console.aws.amazon.com/servicecatalog/home?region=eu-west-2#/home)
- [ ] Select the [*Portfolios*](https://eu-west-2.console.aws.amazon.com/servicecatalog/home?region=eu-west-2#portfolios?activeTab=localAdminPortfolios)
    menu option on the left side and click on the local portfolio created during SWB deployment (e.g. treprod-ldn-pj1)
- [ ] Extract just the ID from *prod-ID* from the list which should contain 4 default SWB products. These ID strings are required in Step 5C

For guidance identifying the default workspace types (products) created by SWB, please refer to the image below.

![SWB Service Catalog Product IDs](../../res/images/Guidance-ServiceCatalogProductsList.png)

### Step 5C. Add Project Budget Control

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [project budget controls](../../src/components/budget_controls/ProjectBudgetControl-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TREProject1ProdBudgetControl". Add the parameters required. Press on button *Next* twice and then press on button *Create stack*

|Parameter Name|Description|Default value|
|:-----------------|:-----------|:-------------|
|BudgetLimit|Estimated annual account spend in USD|*No default - must be specified*|
|BudgetTimeWindow|Choose between an annually or monthly recurring budget|*ANNUALLY*|
|NotificationThresholdActualCost1|Budget threshold percentage for receiving first notification based on actual costs|*80*|
|NotificationThresholdActualCost2|Budget threshold percentage for receiving second notification based on actual costs|*99*|
|NotificationThresholdForecastedCost|Budget threshold percentage for notification based on forecasted costs|*90*|
|ActionThreshold|Budget threshold percentage for stopping new SWB workspace creation based on forecasted costs|*99*|
|BudgetNotifySNSTopicName|The name of the SNS topic whose subscribers (includes TREAdminEmailAddress) receive alerts regarding project budget|*No default - must be specified*|
|TREAdminEmailAddress|The email address for the TRE admin who will receive alerts regarding project budget|*No default - must be specified*|
|SWBStackID|Specify the ID of existing IAM role initial-stack-ID-xacc-env-mgmt|*No default - must be specified*|
|ServiceCatalogProductsList|Leave blank if you want to restrict all SWB workspace types. Otherwise, specify the 4 default products ID (prod-{ID}) from the Service Catalog portfolio created by SWB|*""*|

- [ ] Confirm the stack status is "CREATE_COMPLETE"

When the budget action gets triggered (depends on *AnnualBudgetLimit* and *ActionThreshold*), any allowed user trying to create a new workspace in SWB will see this error message:

![SWB Workspace Creation Expected Failure](../../res/images/Status-DenySWBWorkspaceCreation.png)

### Step 5D - Optional. Adjust Project Budget

Follow these instructions if you need to update the project budget settings.

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Select the stack created in Step 5C and press on button *Update* to adjust the parameters. Please note the changes will take up to 24 hours to reflect in AWS Budgets in terms of alerts and actions.

### Step 5E - Optional. Remove Project Budget Control

Follow these instructions if you need to remove the project budget control policy after e.g. increasing your budget.

- [ ] Go to Service: [AWS Identity and Access Management](https://us-east-1.console.aws.amazon.com/iamv2/home)
- [ ] Select the [*Roles*](https://us-east-1.console.aws.amazon.com/iamv2/home#/roles) menu option on the left side
- [ ] Search for *initial-stack* to locate the role with name *initial-stack-ID-xacc-env-mgmt* (ID is a number)
- [ ] Click on the role identified above and select the policy that has *-DenyCreateWorkSpacePolicy-* in its name
- [ ] Use the *Remove* button on the right side to detach the policy from the role

When the budget control policy has been removed, any allowed user trying to create a new workspace in SWB will see the Available status message:

![SWB Workspace Creation Expected Success](../../res/images/Status-AllowSWBWorkspaceCreation.png)

## Appendix

For further customisations, additional notes can be found below.

- [ ] AWS Budgets limits action types to applying IAM or SCP policies or stopping EC2 and RDS instances.
  For more flexibility, [Amazon SNS can be integrated with AWS Lambda](https://docs.aws.amazon.com/sns/latest/dg/sns-lambda-as-subscriber.html)
  functions to support custom actions when a budget notification is sent.
