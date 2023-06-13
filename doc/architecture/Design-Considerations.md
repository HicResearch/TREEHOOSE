# Design Considerations

---

Below are the key design considerations for TREEHOOSE

## Maintenance

---

- All the core infrastructure is deployed using [IaC (Infrastructure as Code)](https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/infrastructure-as-code.html).
- The solution is based on Serverless Architecture for ease of operability and scalability.

## Audit

---

- [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) is enabled in all AWS accounts
  and the logs centralised for Auditing.
- [AWS Config](https://aws.amazon.com/config/) is enabled in all AWS accounts
  and the config records centralised for Auditing.
- [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) is used for
  log aggregation and metrics for each TRE project/AWS account.

## Security

---

- Use [AWS KMS](https://aws.amazon.com/kms/) for encryption at-rest.
- Encryption in-transit is enabled for all AWS services where applicable
  and also enabled for all API calls.
- For all [AWS IAM](https://aws.amazon.com/iam/) policies the principle of least privilege has been followed.
- [AWS Accounts](https://aws.amazon.com/account/) provide well-defined billing and security boundaries.
  Hence each research project should be hosted in a separate AWS account.

## Considerations for End Users

---

These are some additional decisions that the end user of
TREEHOOSE should make based on their functional and
non-functional requirements.

- Centralise and enable AWS Security services like:

  - [AWS Security Hub](https://aws.amazon.com/security-hub/)
  - [Amazon GuardDuty](https://aws.amazon.com/guardduty/)
  - [Amazon Macie](https://aws.amazon.com/macie/)
  - [AWS IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)

- Enable [AWS Web Application Firewall](https://aws.amazon.com/waf/) for Web Applications.
- Enable additional [Control Tower Guardrails](https://docs.aws.amazon.com/controltower/latest/userguide/guardrails.html).
- Use [Amazon EC2 reserved instances](https://aws.amazon.com/ec2/pricing/reserved-instances/).
- [Optimize](https://docs.aws.amazon.com/whitepapers/latest/best-practices-for-deploying-amazon-appstream-2/cost-optimization.html) how you use AppStream.
