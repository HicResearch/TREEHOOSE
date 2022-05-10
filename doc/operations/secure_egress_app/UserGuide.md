There are 2 types of reviewer personas involved in the Egress App workflow:
1. Information Governance Leads
    - uses a SWB user account of type researcher to create a new workspace to view the contents of the data egress request
    - uses an Egress App user account to provide the 1st approval for a data egress request
1. Research IT Admins
    - uses a SWB user account of type admin to validate that an information governance lead is authorised to grant their approval
    - uses an Egress App user account to provide the 2nd approval for data egress requests, only after the 1st approval has been granted

## Workflow

1. TRE administrator sets up the user accounts as described in the [Configuration Guide](./ConfigurationGuide.md)

1. In the SWB Web App, the Researcher creates and uses a workspace to carry out research activities.

    ![Egress App Workflow - 1](../../../res/images/secure_egress_app/UserGuide-Workflow-1.png)

1. In the SWB Web App, the Researcher adds data to the egress store and submits an egress request from the SWB website.

    ![Egress App Workflow - 2](../../../res/images/secure_egress_app/UserGuide-Workflow-2.png)

    ![Egress App Workflow - 3](../../../res/images/secure_egress_app/UserGuide-Workflow-3.png)

1. The Information Governance Lead receives an email notification about the egress request triggered by the Researcher.

    ![Egress App Workflow - 4](../../../res/images/secure_egress_app/UserGuide-Workflow-4.png)

1. In the Egress Web App, the Information Governance Lead views the egress request searching for the ID from the email notification. Search box is present at the bottom left of the data table.

    ![Egress App Workflow - 5](../../../res/images/secure_egress_app/UserGuide-Workflow-5.png)

1. In the SWB Web App, the Information Governance Lead creates/uses a workspace with the study created in the [Configuration Guide](./ConfigurationGuide.md)

    ![Egress App Workflow - 6](../../../res/images/secure_egress_app/UserGuide-Workflow-6.png)

    ![Egress App Workflow - 7](../../../res/images/secure_egress_app/UserGuide-Workflow-7.png)

1. In the SWB Web App, the Information Governance Lead connects to the workspace to view the egress request contents searching for the ID from the email notification.

    ![Egress App Workflow - 8](../../../res/images/secure_egress_app/UserGuide-Workflow-8.png)

1. In the Egress Web App, the Information Governance Lead approves or rejects the egress request with the ID from the email notification.

    ![Egress App Workflow - 9](../../../res/images/secure_egress_app/UserGuide-Workflow-9.png)

1. If the egress request was rejected by the Information Governance Lead, the Researcher and Information Governance Lead will be notified by email.

    **The steps below happen only if the egress request was approved by the Information Governance Lead.**
    ![Egress App Workflow - 10](../../../res/images/secure_egress_app/UserGuide-Workflow-10.png)

1. If the egress request was approved by the Information Governance Lead, a Research IT Admin will be notified by email.

    ![Egress App Workflow - 11](../../../res/images/secure_egress_app/UserGuide-Workflow-11.png)

1. The Research IT Admin needs to check that the Information Governance Lead approval was granted by a person with the required clearance.

1. In the Egress Web App, the Research IT Admin approves or rejects the egress request with the ID from the email notification.

    ![Egress App Workflow - 12](../../../res/images/secure_egress_app/UserGuide-Workflow-12.png)

1. If the egress request was rejected by the Research IT Admin, the Researcher and Information Governance Lead will be notified by email.

    **The steps below happen only if the egress request was approved by the Research IT Admin.**
    ![Egress App Workflow - 13](../../../res/images/secure_egress_app/UserGuide-Workflow-13.png)

1. If the egress request was approved by the Research IT Admin, the Researcher and Information Governance Lead will be notified by email.

    ![Egress App Workflow - 14](../../../res/images/secure_egress_app/UserGuide-Workflow-14.png)

1. In the Egress Web App, the Information Governance Lead can download the egress request file contents. The number of times a download is allowed is constrained by a parameter set during the Egress App deployment stage.

    ![Egress App Workflow - 15](../../../res/images/secure_egress_app/UserGuide-Workflow-15.png)

1. The Information Governance Lead is responsible for sending the egress request file contents to the Researcher via an approved manual method such as email.
