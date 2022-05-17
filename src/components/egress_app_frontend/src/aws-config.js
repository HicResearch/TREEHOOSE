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
        // oauth: {
        //     domain: `${process.env.REACT_APP_USER_POOL_DOMAIN}`,
        //     scope: ['email','openid','profile', 'aws.cognito.signin.user.admin'],
        //     responseType: 'code',
        //     redirectSignIn: `${process.env.REACT_APP_REDIRECT_SIGNIN_URL}`,
        //     redirectSignOut: `${process.env.REACT_APP_REDIRECT_SIGNOUT_URL}`
        // }
    },
};

export default awsconfig;
