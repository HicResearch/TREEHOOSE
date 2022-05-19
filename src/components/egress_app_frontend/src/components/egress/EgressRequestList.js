// (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
//
// This AWS Content is provided subject to the terms of the AWS Customer Agreement
// available at http://aws.amazon.com/agreement or other written agreement between
// Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.

import React, { useState, useEffect } from 'react';
import '../../style/App.css';
import {
    MDBDataTableV5,
    MDBModal,
    MDBContainer,
    MDBModalBody,
    MDBModalFooter,
    MDBModalHeader,
    MDBInput,
} from 'mdbreact';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Snackbar from '@mui/material/Snackbar';
import SnackbarContent from '@mui/material/SnackbarContent';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import FileDownloadIcon from '@mui/icons-material/FileDownloadRounded';
import ThumbUpRoundedIcon from '@mui/icons-material/ThumbUpRounded';
import ThumbDownRoundedIcon from '@mui/icons-material/ThumbDownRounded';
import CancelRoundedIcon from '@mui/icons-material/CancelRounded';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Stack from '@mui/material/Stack';
import { Button, CircularProgress } from '@mui/material';
import { Auth, API, graphqlOperation } from 'aws-amplify';
import columnHeaders from './columnHeaders';
import { listRequests } from '../../graphql/queries';
import { downloadData, updateRequest } from '../../graphql/mutations';
import awsconfig from '../../aws-config';

function EgressRequestList() {
    const [egressRequestList, setEgressRequestList] = useState({
        columns: [],
        rows: [],
    });

    // Initialise states
    const [showModal, setShowModal] = useState(false);
    const [selectedEgressRequest, setSelectedEgressRequest] = useState([]);
    const [justification, setJustification] = useState('');
    const [decision, setDecision] = useState('');
    const [isEditable, setIsEditable] = useState(false);
    const [isDownloadable, setIsDownloadable] = useState(false);
    const [openNotification, setOpenNotification] = useState(false);
    const [notificationMessage, setNotificationMessage] = useState('');
    const [userRole, setUserRole] = useState('');
    const [userDetails, setUserDetails] = useState({});
    const [downloading, setDownloading] = useState(false);
    const [confirmationOpen, setConfirmationOpen] = useState(false);
    const [confirmed, setConfirmed] = useState(false);

    // Transform backend status
    const formatStatus = (status) => {
        if (status === 'PROCESSING') return 'PENDING';
        return status;
    };

    // Toggles open/close for modal
    const toggleModal = (request) => {
        setShowModal(!showModal);
        if (request !== undefined) {
            setSelectedEgressRequest(request);
            setJustification(request.reason);
        }
    };

    // Fetch all egress requests
    const getAllEgressRequests = async () => {
        const requestsApiResult = await API.graphql(graphqlOperation(listRequests));
        const data = requestsApiResult.data.listRequests;
        const dataLength = data.length;

        if (dataLength !== 0) {
            for (let i = 0; i < dataLength; i += 1) {
                // Format the status to be more user-friendly
                data[i].formattedStatus = formatStatus(data[i].egress_status);
                const request = data[i];
                // Insert button into each row of json for datatable
                data[i].review = (
                    <Button color="primary" variant="contained" onClick={() => toggleModal(request)}>
                        {' '}
                        View
                    </Button>
                );
            }
        } else {
            setNotificationMessage('No available requests to view');
            setOpenNotification(true);
        }
        return data;
    };

    // Determine which user role is assigned, depending on the cognito user group
    const determineRole = (groups) => {
        if (groups.includes(awsconfig.egress_ig_role)) {
            setUserRole('reviewer_1');
        } else if (groups.includes(awsconfig.egress_rit_role)) {
            setUserRole('reviewer_2');
        } else {
            setNotificationMessage('User role cannot be determined. Please contact an administrator');
            setOpenNotification(true);
        }
    };

    // Fetch user's Cognito user group
    const getUserGroup = async () => {
        const user = await Auth.currentAuthenticatedUser();
        const cognitoGroups = user.signInUserSession.idToken.payload['cognito:groups'];

        if (cognitoGroups) {
            determineRole(cognitoGroups);
        } else {
            setNotificationMessage('You are not authorised to access this application');
            setOpenNotification(true);
        }
    };

    // Fetch user's Cognito details
    const getUserDetails = async () => {
        const user = await Auth.currentAuthenticatedUser();
        const username = user.signInUserSession.idToken.payload.email;
        const { email } = user.signInUserSession.idToken.payload;
        setUserDetails({
            user_name: username,
            user_email: email,
        });
    };

    // Call on every state change
    useEffect(() => {
        getAllEgressRequests().then((data) =>
            // Set state using API data and imported headers
            setEgressRequestList({
                columns: columnHeaders,
                rows: data,
            }),
        );
        getUserGroup();
        getUserDetails();
    }, []);

    // Effect to be invoked whenever an egress request is selected i.e. when modal is displayed
    useEffect(() => {
        setIsEditable(
            (selectedEgressRequest.formattedStatus === 'PENDING' && userRole === 'reviewer_1') ||
                (selectedEgressRequest.formattedStatus === 'IGAPPROVED' && userRole === 'reviewer_2'),
        );
        setIsDownloadable(
            Number(selectedEgressRequest.download_count) < awsconfig.max_downloads_allowed &&
                userRole === 'reviewer_1' &&
                selectedEgressRequest.formattedStatus === 'RITAPPROVED',
        );
    }, [selectedEgressRequest, userRole, selectedEgressRequest.download_count]);

    // Check if form is vaid before submission
    const isFormValid = () => {
        if (justification === undefined || justification === null || justification.length < 10) {
            setNotificationMessage('A justification is required (min 10 characters)');
            setOpenNotification(true);
            return false;
        }
        return true;
    };

    // Confirmation dialogue box helper functions
    const handleConfirmationOpen = () => {
        if (isFormValid()) {
            setConfirmationOpen(true);
        }
    };

    const handleConfirmationClose = () => {
        setConfirmationOpen(false);
    };

    const handleConfirmationAgree = () => {
        setConfirmed(true);
        handleConfirmationClose();
    };

    const handleConfirmationDisagree = () => {
        handleConfirmationClose();
    };

    const handleJustificationUpdate = () => (event) => {
        setJustification(event.target.value);
    };

    const handleNotificationClose = () => {
        setOpenNotification(false);
    };

    // Make API call to download API
    const handleDownload = async () => {
        setDownloading(true);
        const count = selectedEgressRequest.download_count == null ? 0 : selectedEgressRequest.download_count;
        const requestDetails = {
            egress_request_id: selectedEgressRequest.egress_request_id,
            workspace_id: selectedEgressRequest.workspace_id,
            download_count: count,
        };

        try {
            const requestsApiResult = await API.graphql(graphqlOperation(downloadData, { request: requestDetails }));

            if (requestsApiResult.data.downloadData !== null) {
                const presignUrl = requestsApiResult.data.downloadData.presign_url;

                // Open presign_url link to download file
                const downloadLink = document.createElement('a');
                downloadLink.download = 'egress_data.zip';
                downloadLink.href = presignUrl;
                downloadLink.click();
                selectedEgressRequest.download_count = Number(selectedEgressRequest.download_count) + 1;
                setDownloading(false);
            } else {
                setNotificationMessage('Download limit exceeded. Please contact an administrator');
            }
        } catch (err) {
            setNotificationMessage('Unable to download. Please try again or contact an administrator');
            setOpenNotification(true);
            setDownloading(false);
        }
    };

    // Make API call to submit egress request review
    const updateEgressRequest = async () => {
        let requestDetails = {};
        const now = new Date();
        const currentDatetime = now.toUTCString();

        if (decision) {
            if (userRole === 'reviewer_1') {
                requestDetails = {
                    egress_request_id: selectedEgressRequest.egress_request_id,
                    task_token: selectedEgressRequest.task_token,
                    ig_reviewer_1_decision: decision,
                    ig_reviewer_1_reason: justification,
                    ig_reviewer_1_email: userDetails.user_email,
                    ig_reviewer_1_name: userDetails.user_name,
                    ig_reviewer_1_dt: currentDatetime,
                };
            } else {
                requestDetails = {
                    egress_request_id: selectedEgressRequest.egress_request_id,
                    task_token: selectedEgressRequest.task_token,
                    ig_reviewer_1_decision: selectedEgressRequest.ig_reviewer_1_decision,
                    rit_reviewer_2_decision: decision,
                    rit_reviewer_2_reason: justification,
                    rit_reviewer_2_email: userDetails.user_email,
                    rit_reviewer_2_name: userDetails.user_name,
                    rit_reviewer_2_dt: currentDatetime,
                };
            }
            try {
                await API.graphql(graphqlOperation(updateRequest, { request: requestDetails }));
                setNotificationMessage('Request saved successfully.');
            } catch (err) {
                setNotificationMessage(err.errors[0].message);
            }
            setOpenNotification(true);
        }
    };

    // Triggers update of request whenever a confirmation on the dialogue box is made
    useEffect(() => {
        if (confirmed) {
            updateEgressRequest();
        }
        setConfirmed(false);
    }, [confirmed]);

    return (
        <>
            <div>
                <div
                    style={{
                        height: 400,
                        width: '100%',
                        paddingLeft: '1%',
                        paddingRight: '1%',
                    }}
                >
                    <MDBContainer>
                        <MDBDataTableV5
                            hover
                            entriesOptions={[5, 20, 25]}
                            entries={5}
                            pagesAmount={4}
                            data={egressRequestList}
                            fullPagination
                            striped
                            btn
                            materialSearch
                        />
                    </MDBContainer>
                </div>
            </div>
            <div>
                <MDBModal isOpen={showModal} toggle={toggleModal} size="xl" centered>
                    <form className="container-fluid">
                        <div className="d-flex justify-content-center" />
                        <MDBModalHeader>
                            <Typography variant="h5" color="primary">
                                Request Details
                            </Typography>
                        </MDBModalHeader>
                        <MDBModalBody>
                            <div className="row">
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Egress Request ID"
                                        id="egress_request_id"
                                        type="text"
                                        value={selectedEgressRequest.egress_request_id}
                                        background
                                    />
                                </div>
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Status"
                                        id="status"
                                        type="text"
                                        value={selectedEgressRequest.formattedStatus}
                                        background
                                    />
                                </div>
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Project ID"
                                        id="project_id"
                                        type="text"
                                        value={selectedEgressRequest.project_id}
                                        background
                                    />
                                </div>
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Workspace ID"
                                        id="workspace_id"
                                        type="text"
                                        value={selectedEgressRequest.workspace_id}
                                        background
                                    />
                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Requested By"
                                        id="requested_by"
                                        type="text"
                                        value={selectedEgressRequest.requested_by}
                                        background
                                    />
                                </div>
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Date Requested"
                                        id="requested_dt"
                                        type="text"
                                        value={selectedEgressRequest.requested_dt}
                                        background
                                    />
                                </div>
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Updated By"
                                        id="updated_by"
                                        type="text"
                                        value={selectedEgressRequest.updated_by}
                                        background
                                    />
                                </div>
                                <div className="col-md-3 ms-auto">
                                    <MDBInput
                                        label="Date Updated"
                                        id="updated_dt"
                                        type="text"
                                        value={selectedEgressRequest.updated_dt}
                                        background
                                    />
                                </div>
                            </div>
                        </MDBModalBody>
                        <Accordion defaultExpanded={userRole === 'reviewer_1'}>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel1a-content"
                                id="panel1a-header"
                            >
                                <Typography variant="h5" color="primary">
                                    Information Governance
                                </Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <MDBModalBody>
                                    <div className="row">
                                        <div className="col-md-4 ms-auto">
                                            <MDBInput
                                                label="Reviewed by"
                                                id="reviewer_1"
                                                type="text"
                                                value={selectedEgressRequest.ig_reviewer_1_email}
                                                disabled={true}
                                                background
                                            />
                                        </div>
                                        <div className="col-md-4 ms-auto">
                                            <MDBInput
                                                label="Date Reviewed"
                                                id="reviewer_1_dt"
                                                type="text"
                                                value={selectedEgressRequest.ig_reviewer_1_dt}
                                                disabled={true}
                                                background
                                            />
                                        </div>
                                        <div className="col-md-4 ms-auto">
                                            <MDBInput
                                                label="Decision"
                                                id="reviewer_1_decision"
                                                type="text"
                                                value={selectedEgressRequest.ig_reviewer_1_decision}
                                                disabled={true}
                                                background
                                            />
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-12">
                                            <MDBInput
                                                label="Justification"
                                                id="reviewer_1_justification"
                                                type="textarea"
                                                rows="4"
                                                value={selectedEgressRequest.ig_reviewer_1_reason}
                                                onChange={handleJustificationUpdate()}
                                                disabled={userRole !== 'reviewer_1' || !isEditable}
                                                outline
                                            />
                                        </div>
                                    </div>
                                </MDBModalBody>
                            </AccordionDetails>
                        </Accordion>
                        <Accordion defaultExpanded={userRole === 'reviewer_2'}>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls="panel1a-content"
                                id="panel1a-header"
                            >
                                <Typography variant="h5" color="primary">
                                    Research IT
                                </Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <MDBModalBody>
                                    <div className="row">
                                        <div className="col-md-4 ms-auto">
                                            <MDBInput
                                                label="Reviewed by"
                                                id="reviewer_2"
                                                type="text"
                                                value={selectedEgressRequest.rit_reviewer_2_email}
                                                disabled={true}
                                                background
                                            />
                                        </div>
                                        <div className="col-md-4 ms-auto">
                                            <MDBInput
                                                label="Date Reviewed"
                                                id="reviewer_2_dt"
                                                type="text"
                                                value={selectedEgressRequest.rit_reviewer_2_dt}
                                                disabled={true}
                                                background
                                            />
                                        </div>
                                        <div className="col-md-4 ms-auto">
                                            <MDBInput
                                                label="Decision"
                                                id="reviewer_2_decision"
                                                type="text"
                                                value={selectedEgressRequest.rit_reviewer_2_decision}
                                                disabled={true}
                                                background
                                            />
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-12">
                                            <MDBInput
                                                label="Justification"
                                                id="reviewer_2_justification"
                                                type="textarea"
                                                rows="4"
                                                value={selectedEgressRequest.rit_reviewer_2_reason}
                                                disabled={userRole !== 'reviewer_2' || !isEditable}
                                                onChange={handleJustificationUpdate()}
                                                outline
                                            />
                                        </div>
                                    </div>
                                </MDBModalBody>
                            </AccordionDetails>
                        </Accordion>
                        <MDBModalFooter>
                            <Stack direction="row" spacing={2}>
                                <Button
                                    color="info"
                                    variant="contained"
                                    startIcon={<CancelRoundedIcon />}
                                    onClick={toggleModal}
                                >
                                    Close
                                </Button>
                                <Button
                                    id="approveBtn"
                                    color="success"
                                    variant="contained"
                                    startIcon={<ThumbUpRoundedIcon />}
                                    onClick={() => {
                                        setDecision('APPROVED');
                                        handleConfirmationOpen();
                                    }}
                                    disabled={!isEditable}
                                >
                                    Approve
                                </Button>
                                <Button
                                    id="rejectBtn"
                                    color="error"
                                    variant="contained"
                                    startIcon={<ThumbDownRoundedIcon />}
                                    onClick={() => {
                                        setDecision('REJECTED');
                                        handleConfirmationOpen();
                                    }}
                                    disabled={!isEditable}
                                >
                                    Reject
                                </Button>

                                {downloading ? (
                                    <CircularProgress size={25} color="primary" />
                                ) : (
                                    <Button
                                        color="primary"
                                        variant="contained"
                                        onClick={handleDownload}
                                        disabled={!isDownloadable}
                                        startIcon={<FileDownloadIcon />}
                                    >
                                        Download
                                    </Button>
                                )}
                            </Stack>
                        </MDBModalFooter>
                    </form>
                    <div>
                        <Snackbar
                            anchorOrigin={{
                                vertical: 'bottom',
                                horizontal: 'left',
                            }}
                            open={openNotification}
                            autoHideDuration={6000}
                            onClose={handleNotificationClose}
                        >
                            <SnackbarContent
                                style={{
                                    backgroundColor: 'blueviolet',
                                }}
                                message={notificationMessage}
                                action={
                                    <IconButton
                                        size="small"
                                        aria-label="close"
                                        color="inherit"
                                        onClick={handleNotificationClose}
                                    >
                                        <CloseIcon fontSize="small" />
                                    </IconButton>
                                }
                            />
                        </Snackbar>
                    </div>
                    <div>
                        <Dialog
                            open={confirmationOpen}
                            onClose={handleConfirmationClose}
                            aria-labelledby="alert-dialog-title"
                            aria-describedby="alert-dialog-description"
                        >
                            <DialogTitle id="alert-dialog-title">Confirmation</DialogTitle>
                            <DialogContent>
                                <DialogContentText id="alert-dialog-description">
                                    Are you sure you want to{' '}
                                    <b>{decision === 'APPROVED' ? 'approve' : 'reject'} this request</b>?
                                </DialogContentText>
                            </DialogContent>
                            <DialogActions>
                                <Stack direction="row" spacing={2} className="confirmation-buttons">
                                    <Button onClick={handleConfirmationDisagree} color="info" variant="contained">
                                        No, Take me back
                                    </Button>
                                    <Button onClick={handleConfirmationAgree} color="success" variant="contained">
                                        Yes I&quot;m sure
                                    </Button>
                                </Stack>
                            </DialogActions>
                        </Dialog>
                    </div>
                </MDBModal>
            </div>
        </>
    );
}

export default EgressRequestList;
