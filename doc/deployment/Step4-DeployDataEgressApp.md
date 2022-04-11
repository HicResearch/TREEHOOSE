Ensure all steps below are executed in AWS region: [London (eu-west-2)](https://eu-west-2.console.aws.amazon.com/).

If this add-on application is added, a researcher can use a GUI-based data egress approval workflow to take out data from the TRE with the permission of multiple parties (Information Governance Lead, Research IT).

## Prerequisites

Apply these prerequisites only to accounts part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.

### Remove email restrictions

By default, a new AWS account will be placed in the [Amazon SES](https://aws.amazon.com/ses/) sandbox which enforces a set of restrictions.

To enable the app to send emails to the relevant already-approved parties (information governance leads, IT admins and researchers), an admin must also manually add each email as a verified entity in SES and the person with the email address must confirm the registration using the link received in an email.

To skip the need to manually add and verify each email address in Amazon SES, you should request production access to SES by following these [instructions](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html).

## Step 4. Deploy Data Egress App

**Time to deploy**: Approximately ? minutes

Apply these steps only to accounts part of the **TRE Projects Prod** OU.

Log in to the [AWS Management Console](https://console.aws.amazon.com/) using your **TRE Project 1 Prod** account and Admin privileges.
