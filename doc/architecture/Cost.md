# Cost

---

You are responsible for the cost of the AWS services used to run this solution.
As of January 2022, the cost for running this solution with the default settings
in the EU West (Ireland) AWS Region is approximately **$30** for TRE account with all add-ons.
Prices are subject to change.
For full details, see the pricing page for each AWS service used in this solution.

> **_NOTE:_**  Many AWS Services include a Free Tier – a baseline amount of the service that customers can use at no charge.
> Actual costs may be more or less than the pricing examples provided.

The baseline cost is just for spinning up the infrastructure.
As the solution is based on Serverless architecture, you only
pay for what you use when you use.

Following factors will contribute to incremental costs for an actively used deployment or TRE account:

- Compute resources used by researchers in the form
  of EC2 instances
- Volume of data stored in S3 buckets in the Data Lake account
- AppStream resources used by researchers to interact
  with their research workspace
- Volume of backup data stored by AWS Backup

The cost of using and maintaining an AWS Control Tower
environment can be found [here](https://aws.amazon.com/controltower/pricing/).

The best place to calculate the cost of using this solution
is by using [AWS Pricing Calculator](https://calculator.aws/#/)
and putting in the correct usage information.

## Example cost table

---

The following table provides an example cost breakdown for deploying this
solution with the default settings in EU West (Ireland) AWS Region.

### Base Installation

An installation of TRE without any workspaces and users.

|AWS Service|Monthly cost|
|----|----|
|Networking services|$11|
|KMS|$6|
|Config|$4|
|CloudTrail|$3.5|
|EC2-other|$1.5|
|DynamoDB|$6|
|Service Catalog|$1|
|Step Functions|$0.09|
|Lambdas|$0.003|
|CloudFront|$0.0002|
|CloudWatch|$0.0003|
|Total|$33.0935|

### EC2 Usage

Below example is based on on-demand
pricing.
A researcher uses a workspace for 730 hours.

Example - 1
|AWS Service|Monthly cost|
|----|----|
|EC2 - t3.large|$66.58 |
|EBS - 10GB| $1.10|
|Total|$67.68|

Example - 2
|AWS Service|Monthly cost|
|----|----|
|EC2 - m6g.8xlarge|$1,004.48 |
|EBS - 80GB| $8.80|
|Total|$1,013.28|

### SageMaker Usage

A researcher use sagemaker notebook
for 730 hours on a project.

Example
|AWS Service|Monthly cost|
|----|----|
|SageMaker - notebook - ml.c5.large| $82.80|
|Total|$82.80|

### S3 storage

A researcher works on a 1 TB data study
and produces a 10 GB output to download

Example
|AWS Service|Monthly cost|
|----|----|
|S3 - study data| $23.58 |
|Data Egress| $0.90|
|Total|$24.48|

All cost examples provided above are indicative.
