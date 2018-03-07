# Aws stuff

## Deploy lambda

```bash
awslocal --endpoint-url=http://localhost:4574 \
                                            lambda \
                                            create-function --function-name=lambda_queue \
                                            --runtime=python3.5 \
                                            --role=lambda_policy \
                                            --handler=app.lambda_handler \
                                            --zip-file fileb://lambda.zip
{
    "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:lambda_queue",
    "FunctionName": "lambda_queue",
    "TracingConfig": {},
    "Environment": {
        "Variables": {},
        "Error": {}
    },
    "Handler": "app.lambda_handler",
    "VpcConfig": {
        "SubnetIds": [
            null
        ],
        "SecurityGroupIds": [
            null
        ]
    },
    "Role": "lambda_policy",
    "Runtime": "python3.5"
}
```

## Generate modules

```bash
python3 -m pip install -r lambda/requirements.txt -t lambda/
```

## Create apigateway

```bash
awslocal apigateway create-rest-api --name 'Lambda rest API'
{
    "createdDate": 1520431102,
    "id": "06A-Z3A-ZA-Z3695",
    "name": "Lambda rest API"
}
```

## Get id above to check the resources

```bash
awslocal apigateway get-resources --rest-api-id 06A-Z3A-ZA-Z3695
{
    "items": [
        {
            "resourceMethods": {
                "GET": {}
            },
            "path": "/",
            "id": "44539A-Z2568"
        }
    ]
}
```

## add lambda to apigateway

```bash

awslocal lambda list-functions
{
    "Functions": [
        {
            "FunctionName": "hello_world",
            "CodeSize": 50,
            "Handler": "app.lambda_handler",
            "Version": "$LATEST",
            "Environment": {},
            "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:hello_world",
            "Runtime": "python3.5"
        }
    ]
}

awslocal apigateway put-integration \
            --rest-api-id 06A-Z3A-ZA-Z3695 \
            --resource-id 44539A-Z2568 \
            --http-method GET \
            --type AWS \
            --integration-http-method GET \
            --uri aws:lambda:us-east-1:000000000000:function:hello_world

awslocal apigateway create-deployment \
                --rest-api-id 06A-Z3A-ZA-Z3695 \
                --stage-name prod
```

## Create s3 bucket

```bash
awslocal s3 mb s3://test
```

## Create stack using cloudformation

```bash
awslocal cloudformation create-stack --template-body file://cloudformation_templates/template.yaml --stack-name sqs
```

```bash
lambda invoke \
        --invocation-type Event \
        --function-name hello_world \
        outputfile.txt
```