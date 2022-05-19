// (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
//
// This AWS Content is provided subject to the terms of the AWS Customer Agreement
// available at http://aws.amazon.com/agreement or other written agreement between
// Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.

const columnHeaders = [
    {
        label: 'ID',
        field: 'egress_request_id',
        sort: 'asc',
        width: 70,
    },
    {
        label: 'Project ID',
        field: 'project_id',
        sort: 'asc',
        width: 70,
    },
    {
        label: 'Researcher',
        field: 'requested_by',
        sort: 'asc',
        width: 70,
    },
    {
        label: 'Date',
        field: 'requested_dt',
        sort: 'asc',
        width: 70,
    },
    {
        label: 'Status',
        field: 'formattedStatus',
        sort: 'asc',
        width: 70,
    },
    {
        label: 'View',
        field: 'review',
        width: 70,
    },
];

export default columnHeaders;
