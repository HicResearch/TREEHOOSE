# Egress App Front-End

- [Egress App Front-End](#egress-app-front-end)
  - [Egress Frontend Solution](#egress-frontend-solution)
    - [App.js](#appjs)
    - [components/egress/EgressRequestList.js](#componentsegressegressrequestlistjs)
    - [components/egress/columnHeaders.js](#componentsegresscolumnheadersjs)
    - [components/topBar/Topbar.jsx](#componentstopbartopbarjsx)
    - [graphql](#graphql)
  - [GraphQL Schema Change](#graphql-schema-change)
  - [Component Libraries](#component-libraries)
  - [Available Scripts](#available-scripts)
    - [`npm start`](#npm-start)
    - [`npm start:local`](#npm-startlocal)
    - [`npm test`](#npm-test)
    - [`npm build`](#npm-build)
    - [`npm eject`](#npm-eject)
    - [`npm pipeline`](#npm-pipeline)
  - [Learn More](#learn-more)
    - [Code Splitting](#code-splitting)
    - [Analyzing the Bundle Size](#analyzing-the-bundle-size)
    - [Making a Progressive Web App](#making-a-progressive-web-app)
    - [Advanced Configuration](#advanced-configuration)
    - [Deployment](#deployment)
    - [npm build fails to minify](#npm-build-fails-to-minify)

The **Egress web application** is an add-on solution that enables management of data egress requests
 from the Trusted Research Environment (TRE).

The front-end is a single page web application built with [React](https://reactjs.org/).

## Egress Frontend Solution

The source code for the egress app frontend contains all the JavaScript, HTML, and GraphQL code required
 to build and deploy the application.

Scripts and folders of importance:

### App.js

The root of the application which provides the entry point for all the components and where
 top level imports are defined.

### components/egress/EgressRequestList.js

This file contains the code required to render the egress requests in the form of a table, while providing
 sort and search capabilities. On render, the script makes an API call to
 [AWS AppSync](https://aws.amazon.com/appsync/) to fetch the egress requests from the database. The script
 also interacts with another API to allow for download of egress request objects.

To render webpage components such as the table, buttons, and modals, the React library called
 [Material Design for Boostrap](https://mdbootstrap.com/docs/react/) is utilised.

### components/egress/columnHeaders.js

Column headers of the egress request table are predefined here.
>Note: To add/remove headers rendered on the page, you can modify this file

### components/topBar/Topbar.jsx

This file contains the code to render the top header bar on the page which contains the application title.

### graphql

This folder contains all of the graphql scripts and components to interact with the AppSync API.
 The *schema.graphql* contains the schema definition of the API

The *mutations.js* and *queries.js* scripts contain the GraphQL code, which the webapp uses
 to fetch or modify data from the API.

## GraphQL Schema Change

>Note: This requires installation of Amplify CLI - [instructions](https://docs.amplify.aws/cli/start/install)

1. Any changes to the GraphQL schema should be made inside
 *src/components/egress_app_backend/egress_backend/graphql/schema.graphql* in the backend.
1. Remove any existing files inside *src/components/egress_app_frontend/src/graphql/schema.graphql*
 in the frontend.
1. Copy the *schema.graphql* from the backend to *src/components/egress_app_frontend/src/graphql/schema.graphql*
 in the frontend.
1. Run the command `amplify add codegen` in *src/components/egress_app_frontend/src/graphql* to generate
 the updated models
 for the frontend client to use.
1. You should see updated *queries.js* and *mutations.js* files in the same location.

## Component Libraries

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

>Note: The web app will run with limited functionality, as there is no integration with AppSync or Cognito.

### `npm start:local`

Runs the app in development mode with **Cognito and AppSync integration**.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

>Note: This requires a *.env.local* file in the frontend source code directory, which contains
>all of the integration endpoints. The integration endpoints can be found under *Environment
>variables in the Amplify management console*.

Format of the **'.env.local'** file:

```console
REACT_APP_APPSYNC_API=
REACT_APP_REGION=
REACT_APP_USER_POOL_CLIENT_ID=
REACT_APP_USER_POOL_ID=
REACT_APP_USER_POOL_DOMAIN=
```

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests)
 for more information.

### `npm build`

Builds the app for production to the `build` folder.
It bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes. Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment)
 for more information.

### `npm eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time.
 This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc)
 right into your project so you have full control over them. All of the commands except `eject` will still work,
 but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments,
 and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful
 if you couldn’t customize it when you are ready for it.

### `npm pipeline`

This will run a series of commands to lint the
code using [eslint](https://eslint.org/), check code formatting
using [prettier](https://prettier.io/) and
`npm audit` & `npm outdated` to run node package manager audit.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

To learn about code splitting, view this [guidance](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

To learn about analysing the bundle size, view this [guidance](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

To learn about making a progressive web app, view this [guidance](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

To learn about advanced configurations, view this [guidance](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

To learn about deployments, view this [guidance](https://facebook.github.io/create-react-app/docs/deployment)

### npm build fails to minify

To troubleshoot issues when npm build fails to minify, view this [guidance](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
