// (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
//
// This AWS Content is provided subject to the terms of the AWS Customer Agreement
// available at http://aws.amazon.com/agreement or other written agreement between
// Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.

const awsconfig = {
    aws_appsync_graphqlEndpoint: `${process.env.REACT_APP_APPSYNC_API}`,
    aws_appsync_region: `${process.env.REACT_APP_REGION}`,
    aws_appsync_authenticationType: 'AMAZON_COGNITO_USER_POOLS',
    egress_ig_role: `${process.env.REACT_APP_EGRESS_IG_ROLE}`,
    egress_rit_role: `${process.env.REACT_APP_EGRESS_RIT_ROLE}`,
    max_downloads_allowed: `${process.env.REACT_APP_MAX_DOWNLOADS_ALLOWED}`,
    Auth: {
        region: `${process.env.REACT_APP_REGION}`,
        userPoolId: `${process.env.REACT_APP_USER_POOL_ID}`,
        userPoolWebClientId: `${process.env.REACT_APP_USER_POOL_CLIENT_ID}`,
    },
};

export default awsconfig;
