# Data Lake

The TREEHOOSE TRE solution contains a data lake that needs to be deployed
 with every TRE project. The data lake is used to store and manage datasets in an
 environment which can be governed securely.

## Data Ingestion

[Amazon S3](https://aws.amazon.com/s3/) provides a cost-effective way to store
 large amounts of data in an easy-to-use secure way. The data lake deployed
 uses S3 buckets to store datasets and results for research activities.

Data Lake Managers are responsible for uploading datasets into the data lake
 and ensuring the data has been processed and it's ready for research activities.

The **TRE Source Bucket** is created after
 [deploying the data lake](../deployment/Step3-CreateDataLake.md) and is registered
 with [AWS Lake Formation](https://aws.amazon.com/lake-formation/). Data Lake Managers
 can use this encrypted bucket to store data suitable as input for research activities.

Data Lake Managers can upload data to the **TRE Source Bucket** using
 [multiple methods](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html)
 that are available for S3. When uploading large files to S3, they can leverage available
 [optimisation methods](https://aws.amazon.com/premiumsupport/knowledge-center/s3-upload-large-files/).

Optionally, Data Lake Managers:
* can apply ETL jobs on S3 buckets using [AWS Glue](https://aws.amazon.com/glue/) to prepare
 or transform the data before they store it in the **TRE Source Bucket** to share it with researchers.
* can query S3 data buckets like **TRE Source Bucket** using [Amazon Athena](https://aws.amazon.com/athena)
 and store the results in another S3 bucket e.g. **TRE Analyst Bucket**

To learn more about Amazon S3, check the
 [official user guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html).

To learn more about AWS Glue, check the
 [official documentation](https://docs.aws.amazon.com/glue/index.html).

To learn more about Amazon Athena, check the
 [official user guide](https://docs.aws.amazon.com/athena/latest/ug/getting-started.html).

## Data Usage

