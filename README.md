# TREEHOOSE

---

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

[![Apache License 2.0](https://badgen.net/badge/license/Apache%20License%202.0/blue)](./LICENSE)
![Release Alpha](https://badgen.net/badge/release/Alpha/orange)

DARE UK Sprint Project: Trusted Research Environment and Enclave for Hosting
Open Original Science Exploration

## What is TREEHOOSE

Trusted Research Environments(TREs) are used by many organisations to securely
manage sensitive data for research.

TREEHOOSE is an open-source platform for deploying TREs on Amazon Web Services
(AWS). It will include open-source tooling to streamline building and operating
TREs on public cloud infrastructure whilst maintaining security and trust.

The recent
[Goldacre Review ("Better, Broader, Safer: Using Health Data for Research and Analysis")](https://www.goldacrereview.org/)
highlighted the need for standardisation across TREs, ideally through the use of
open-source infrastructure.

### Development status

TREEHOOSE is under active development. It is suitable for anyone interested in
deploying a trusted research environment on AWS. Currently it has good support
for launching customised Windows Desktops, and limited support for Linux
workspaces with SSH access. All access is managed through a TRE web interface
which prevents unauthorised egress of confidential data.

Features include automated backups for researcher workspaces, secure egress
requiring approvals from data governors or other authorised personnel, and
budget alerts to help manage spending.

You can deploy a TRE on your own following the TREEHOOSE documentation, but due
to the active development we strongly encourage you to get in touch with us
first, either by
[opening a GitHub issue on this repository](https://github.com/HicResearch/TREEHOOSE/issues)
or by emailing `hicsupport@dundee.ac.uk`.

We can help demonstrate features of the platform and see how they match your requirements,
and discuss future enhancements.

---

## Use cases

TREEHOOSE is originally developed for use with confidential healthcare data such
as patient medical records, but is designed to be used and customised for all
research and analysis disciplines.

---

## Documentation

The documentation is divided into several sections:

- [Architecture](./doc/architecture/README.md)
- [Security](./doc/security/SecurityControls.md)
- [Deployment](./doc/deployment/README.md)
- [Operations](./doc/operations/README.md)
- [Troubleshooting](./doc/troubleshooting/TroubleshootingRunbook.md)

---

## Contributing

The main purpose of this repository is to continue evolving TREEHOOSE, making it
faster and easier to use. Development of TREEHOOSE happens in the open on
GitHub, and we are grateful to the community for contributing bugfixes and
improvements. Read below to learn how you can take part in improving TREEHOOSE.

### [Code of Conduct](CODE_OF_CONDUCT.md)

TREEHOOSE has adopted a Code of Conduct that we expect project participants to
adhere to. Please read the full text so that you can understand what actions
will and will not be tolerated.

### [Contributing Guide](CONTRIBUTING.md)

Read our contributing guide to learn about our development process, how to
propose bugfixes and improvements, and how to integrate your changes in this
repository.

---

## License

This project is licensed under the [Apache-2.0 License](./LICENSE).
