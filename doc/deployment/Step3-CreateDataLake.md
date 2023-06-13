# Data Lake Deployment

Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

## Step 3. Deploy Data Lake

**Time to deploy**: Approximately 5 minutes

Due to design considerations, each account in the **TRE Data Prod** OU must contain only one data lake.

Do not create a Datalake in the main (**TRE Project 1 Prod**) account, you will not be able to use it in the TRE.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Datalake 1 Prod**
account and Admin privileges.

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [_Stacks_](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks)
      menu option on the left side
- [ ] Press button:
      [_Create Stack_ with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option _Upload a template file_ to upload CloudFormation template file: [data lake](../../src/data_lake/DataLake-Cfn.yaml)
      and press on button _Next_
- [ ] Provide _Stack name_: "TREDataLake1". Add the parameters required. Press on button _Next_ twice
      and then press on button _Create stack_

| Parameter Name   | Description                                                                                               | Default value                    |
| ---------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------- |
| EgressAppAccount | Account number which is hosting the Egress add-on application (Add **TRE Project 1 Prod** account number) | _No default - must be specified_ |
| LFDatabaseName   | Lake Formation database name that will be created                                                         | _No default - must be specified_ |

- [ ] Confirm the stack status is "CREATE_COMPLETE"

Tip: If you are adding data to the bucket you may need to enforce encryption (`aws s3 cp --sse aws:kms`) or the action may be rejected.
