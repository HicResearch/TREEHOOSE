# Uninstallation Guide

---

## Clean-Up Notes

### Delete the Workspace Backups resources

Locate the CloudFormation stack deployed in Step 6 (Step 6B. Deploy backend infrastructure) and delete it by following these [instructions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).

### Delete the Project Budget Controls resources

Locate the CloudFormation stack deployed in Step 5 (Step 5C. Add Project Budget Control) and delete it by following these [instructions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).

### Delete Egress App frontend resources

Locate the CloudFormation stack deployed in Prerequisites (Step 5. Create placeholder Amplify App) and delete it by following these [instructions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).

### Delete Egress App backend resources

Locate the CloudFormation stack deployed in Step 4 (Step 4C. Deploy backend infrastructure) and delete it by following these [instructions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).

### Delete data lake resources

Locate the CloudFormation stack deployed in Step 3 and delete it by following these [instructions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).

### Uninstall ServiceWorkbench

ServiceWorkbench was deployed in Step 2.

Follow the official [instructions](https://github.com/awslabs/service-workbench-on-aws/blob/mainline/docs/Service_Workbench_Installation_Guide.pdf.) provided by the ServiceWorkbench team to delete the associated resources.

### Delete the Deployment Instance

Locate the CloudFormation stack deployed in Step 1 and delete it by following these [instructions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).
