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
