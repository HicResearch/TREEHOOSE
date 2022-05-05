# Design Considerations

---

Below are the key design considerations for TREEHOOSE

## Maintenance

---

- All the core infrastructure is deployed using IaC (Infrastructure as Code).
- Maximised the use of AWS Serverless services for ease of operability and scalability.

## Audit

---

- [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) is enabled in all AWS accounts
  and the logs centralised for Auditing.
- [AWS Config](https://aws.amazon.com/config/) is enabled in all AWS accounts
  and the config records centralised for Auditing.

## Security

---

- Use [AWS KMS](https://aws.amazon.com/kms/) for encryption at-rest.
- Encryption in-transit is enabled for all AWS services where applicable
  and also enabled for all API calls.
- For all [AWS IAM](https://aws.amazon.com/iam/) policies principle of least privilege has been followed.
