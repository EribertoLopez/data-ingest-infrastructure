# data-ingest-infrastructure
Infrastructure code ([Serverless Framework](https://www.serverless.com/framework/docs/)) for unified data ingest on AWS.

### Overview
```
├── README.md
├── lambdas <-- Put your custom data processing lambda function/module
│   ├── app.py <-- Contains the Kinesis stream consumer
│   └── dataservice.py 
├── policies
│   └── globalPolicies.yml
├── requirements.txt <-- Add lambda dependencies
├── resources
│   ├── BucketPolicy.yml
│   ├── IngestDataS3.yml
│   ├── KinesisEvent.yml
│   ├── KinesisStream.yml
│   └── MessageBackUpS3.yml
├── serverless.env.yml <-- Define serverless.yml env variables
└── serverless.yml <-- Magically gets picked up by serverless framework CLI
```

### Getting Started
- Install the Serverless Framework binary by following https://www.serverless.com/framework/docs/getting-started/
    - Once installed use `serverless help` to list the commands available
    - Use `$ source install.sh` to install the necessary plugins in `serverless.yml`
- Install and configure the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
    - Once installed configure your CLI to use the profile of your choice `$ aws configure`

### Contributing
- When adding a new lambda function:
    - place the lambda function in the `/lambdas` directory
    - Make sure that the `iamRoleStatements` gives your new function enough permissions
    - Finally, add your new lambda to the `serverless.yml`
    ```
    myNewLambda:
        handler: lambdas/dataservice.myNewLambda # Name of the function in module
        events:
        - http:
            path: /myNewLambdaEndpoint # Name of the endpoint that will trigger function
            method: post
    ```
- When adding a new Resource:
    - Create a `myNewResource.yml` and place it in the `/resources` directory
    - Next, add it the the `serverless.yml` 
    ```
    resources:
      Resources:
        myNewResource: ${file(./resources/myNewResource.yml)}

    ```
- When adding a new Policy:
    - Create a `myNewpolicy.yml` and place it in the `/polices` directory
    - Next, add it the the `serverless.yml` 
    ```
    iamRoleStatements: ${file(./polices/myNewpolicy.yml)}
    ```


### Deployment
- Make sure to have your AWS CLI configured to the appropriate profile
- Prior to deployment we must package an artifact that will be uploaded to a Serverless Framework managed S3. This artifact will be used in the creation of the cloudformation stack for this deployment.
    - `$ serverless package`
- Next, use `$ serverless deploy` to deploy the cloudformation stack

### Kinesis Stream Testing
- Use the `kinesisEvent.sh` in the `/tests` directory to send message to the kinesis stream.
    - ie: `$ source tests/kinesisEvent.sh`