# TRE Data Lake

The TREEHOOSE TRE solution contains a data lake that needs to be deployed with every TRE project.
It is used to store and manage datasets in an environment which can be governed securely.

The pre-configured data lake is created with the CloudFormation template provided as source code.

## Services

### Amazon Simple Storage Service (S3)

[Amazon S3](https://aws.amazon.com/s3/) provides the storage for the data in the data lake
in a cost-effective easy-to-use way.

There are 5 S3 buckets created:

1. TRE Source Bucket

   - Can store input datasets for research activities
   - Can be attached to SWB as a registered data study
   - Can be used in data transformation pipelines to manage e.g. sensitive datasets

1. TRE Target Bucket

   - Stores the approved egressed data from research activities
   - Used by the Egress Addon web application

1. TRE Analyst Bucket

   - A data analyst can run queries using [Amazon Athena](https://aws.amazon.com/athena)
     on the data and store query results here

1. TRE Lake Admin Bucket

   - A data lake administrator can run queries using [Amazon Athena](https://aws.amazon.com/athena)
     on the data and store query results here

1. TRE Access Logs Bucket
   - S3 access logging destination for the other buckets

Each of the data S3 buckets:

- Blocks public access

- Is encrypted at-rest

- Has versioning enabled

- Has access logging configured

### AWS Identity and Access Management (IAM)

[AWS IAM](https://aws.amazon.com/iam/) provides fine-grained access control to other AWS services.

Some resources in this template have IAM policies attached to control access or enforce security
constraints. For example, the S3 buckets will deny attempts to upload data in unencrypted form
and expect the use of KMS keys for server-side encryption.

There are 5 IAM roles created:

1. TREAdminRole

- Has PowerUser access
- Can manage KMS keys but cannot use the keys

1. TREDataAnalystRole

- Can read data in the TRE Source Bucket and execute Amazon Athena queries
- Can put query results in the TRE Analyst Bucket

1. TREDataLakeAdminRole

- The designated Lake Formation administrator with full access to the Data Lake
- Can use KMS keys but cannot manage or perform administrative tasks on KMS keys

1 TRELFRegisterLocationServiceRole

- Needed to register TRE Source Bucket and TRE Target Bucket with AWS Lake Formation

1. TREGlueRole

- Role used by AWS Glue for Glue jobs and crawlers

### AWS Key Management Service (KMS)

[AWS KMS](https://aws.amazon.com/kms/) is a place to create and manage cryptographic keys.

Each of the S3 buckets is encrypted server-side with its dedicated KMS encryption key which has rotation enabled.

### AWS Glue

[AWS Glue](https://aws.amazon.com/glue/) makes data discovery and preparation easy to simplify data integration.

An AWS Glue database is created which will be used to catalog metadata about data sources. This is the initial phase
of the long-term vision of exposing a catalog of datasets available within the data lake so that researchers can
request access to datasets that are of interest to them.

### AWS Lake Formation

[AWS Lake Formation](https://aws.amazon.com/lake-formation/) creates a secure data lake from the data sources
provided and applies access and security policies. It builds on the capabilities provided by Amazon S3 and
AWS Glue.

The TRE Source and TRE Target S3 buckets are registered as data lake locations. Once S3 buckets
(or any other supported data sources) are registered with AWS Lake Formation, the service can be used to
provide fine-grained access to both the data catalogs and the underlying data being described by the catalog.
