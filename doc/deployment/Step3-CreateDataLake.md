Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

## Step 3. Deploy Data Lake

**Time to deploy**: Approximately 5 minutes

Due to design considerations, each account in the **TRE Data Prod** OU must contain only one data lake.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Datalake 1 Prod** account and Admin privileges.

- [ ] Go to Service: [AWS CloudFormation](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/)
- [ ] Select the [*Stacks*](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks) menu option on the left side
- [ ] Press button: [*Create Stack* with new resources](https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/template)
- [ ] Select option *Upload a template file* to upload CloudFormation template file: [data lake](../../src/data_lake/DataLake-Cfn.yaml) and press on button *Next*
- [ ] Provide *Stack name*: "TREDataLake1". Add the parameters required. Press on button *Next* twice and then press on button *Create stack*

|Parameter Name|Description|Default value|
|-----------------|-----------|-------------|
|EgressAppDomainName|Use value from Prerequisites Step 5 - Egress app domain name as allowed origin for CORS configuration attached to TRETargetBucket (e.g. https://<branch>.<app_id>.amplifyapp.com)|*No default - must be specified*|
|EgressAppAccount|Account number which is hosting the Egress add-on application (Add **TRE Project 1 Prod** account number)|*No default - must be specified*|
|EgressAppStackName|Part of the Egress add-on application: Stack name used for the Egress-Backend|*No default - must be specified*|
|EgressAppCopyLambdaPrefix|Prefix for the lambda function which copies approved egress data to the data lake|*EgressAppCopyLambdaPrefix*|
|EgressAppDownloadLambdaPrefix|Prefix for the lambda function which downloads approved egress data from the data lake|*EgressApiLambdaServiceRole*|
|LFDatabaseName|Lake Formation database name that will be created|*No default - must be specified*|

- [ ] Confirm the stack status is "CREATE_COMPLETE"
