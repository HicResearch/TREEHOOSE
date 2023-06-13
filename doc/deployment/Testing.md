# Acceptance testing

This is a manual process performed after deployment to check the TRE is working correctly.
These tests should be done by an admin, taking on the different roles.

Prerequisites: a researcher user with access to study data has been created.

## Workspaces

Perform the following tests for Linux and Windows workspaces

- A researcher can launch workspaces
- A researcher can connect to a workspaces
- A researcher can see their study data in the workspaces
- A researcher cannot make network requests to external (internet) resources

### Egress (researcher)

- A researcher can copy files to the egress folder, and can request egress

### Egress (administrators)

- A notification is received when a researcher requests egress
- An information governor (IG) can launch a workspace with access to all egress requests
- An IG can approve or deny an egress request
- If an IG approves a request a notification is sent to the IT administrator
- The IT admin can approve or deny an egress request
- If the IT admin approves the request the IG can download the egressed files in the egress app
