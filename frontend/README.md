## Project overview

This blueprint creates a [React](https://reactjs.org/) SPA (single-page application) project. The project uses the CodeCatalyst Labs action "Deploy to AWS Amplify Hosting" to deploy to [AWS Amplify Hosting](https://aws.amazon.com/amplify/hosting/).

### Architecture overview

A (SPA) single-page application is a web application implementation that loads a web document and updates it by using JavaScript APIs. Your customers can then use your website without loading entire pages from the server, which helps improve your website's performance and provides a more dynamic user experience. 

The deployment pipeline deploys the SPA to an Amazon CodeCatalyst environment. The Amazon CodeCatalyst environment requires an AWS account connection for your Amazon CodeCatalyst space and a configured IAM role for your project workflow. After you create your project, you can view the repository, source code, and CI/CD workflow for your Amazon CodeCatalyst project. After your workflow runs successfully, you can access your deployed application URL in the output of your workflow.

### Web application framework

**[React](https://reactjs.org/)** - powered by [Create React App](https://create-react-app.dev/)

### Hosting



**AWS Amplify Hosting**

[AWS Amplify Hosting](https://aws.amazon.com/amplify/hosting/) offers a fully managed hosting service for web apps and static websites that can be accessed directly from the AWS console.

![AWS Amplify Architecture Diagram](https://deyn4asqcu6xj.cloudfront.net/create-spa-amplify-hosting.png)

## Connections and permissions

You can create a new account connection from the AWS accounts menu in your Amazon CodeCatalyst space. AWS IAM roles added to the account connection are used to authorize project workflows to access AWS account resources.

Expected role capabilities: *CodeCatalyst**

## Project resources

This project contains the following folders:

- root - The web application

This project has created the following Amazon CodeCatalyst Resources:

- A source repository
- An environment
- A workflow for verifying pull requests at .codecatalyst/workflows/onPullRequestBuildAndTest.yaml
- A workflow for deploying changes pushed to main at .codecatalyst/workflows/onPushToMainPipeline.yaml

### Cleaning up resources

To cleanup the resources created by this project delete the stack that the "Deploy to AWS Amplify Hosting" action created. To delete the stack use the AWS CloudFormation console in the AWS account you associated when you launched the blueprint. To find the stack name refer to the workflow, if you used the default stack name it will be DevelopmentFrontendStack-XXXXX.

## Additional resources

See the Amazon CodeCatalyst user guide for additional information on using the features and resources of Amazon CodeCatalyst

---

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
