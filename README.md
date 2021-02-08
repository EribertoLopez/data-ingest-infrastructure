# data-ingest-infrastructure
Infrastructure code ([Serverless Framework](https://www.serverless.com/framework/docs/)) for unified data ingest on AWS.

### Overview

### Getting Started
- Install the Serverless Framework binary by following https://www.serverless.com/framework/docs/getting-started/
    - Once installed use `serverless help` to list the commands available
- Install and configure the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
    - Once installed configure your CLI to use the profile of your choice `$ aws configure`

### Deployment
- Make sure to have your AWS CLI configured to the appropriate profile
- Prior to deployment we must package an artifact that will be uploaded to a Serverless Framework managed S3. This artifact will be used in the creation of the cloudformation stack for this deployment.
    - `$ serverless package`
- Next, use `$ serverless deploy` to deploy the cloudformation stack

