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
    * Stores the input datasets for research activities
    * Attached to SWB as a registered data study made available in
    compute workspaces for research activities

1. TRE Target Bucket
    * Stores the approved egressed data from research activities
    * Accessed by the Egress Addon web application

1. TRE Analyst Bucket

1. TRE Lake Admin Bucket

1. TRE Access Logs Bucket
    * S3 access logging destination for the other buckets

Each of the data S3 buckets:

* Blocks public access

* Is encrypted at-rest

* Has versioning enabled

* Has access logging configured

### AWS Identity and Access Management (IAM)

[AWS IAM](https://aws.amazon.com/iam/) provides fine-grained access control to other AWS services.

Some resources in this template have IAM policies attached to control access or enforce security
 constraints. For example, the S3 buckets will deny attempts to upload data in unencrypted form
 and expect the use of KMS keys for server-side encryption.

### AWS Key Management Service (KMS)

[AWS KMS](https://aws.amazon.com/kms/) is a place to create and manage cryptographic keys.

Each of the S3 buckets is encrypted server-side with its dedicated KMS encryption key which has rotation enabled.

### AWS Glue

[AWS Glue](https://aws.amazon.com/glue/) makes data discovery and preparation easy to simplify data integration.

The data in the S3 buckets can be optionally scanned and processed using Glue.

### AWS Lake Formation

[AWS Lake Formation](https://aws.amazon.com/lake-formation/) creates a secure data lake from the data sources
 provided and applies access and security policies. It builds on the capabilities provided by Amazon S3 and
 AWS Glue.

 The TRE Source and TRE Target S3 buckets are registered as data lake locations.

 A predefined set of permissions is added to the Data lake permissions table.
