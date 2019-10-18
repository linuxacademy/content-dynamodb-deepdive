# 6.1.2 - Triggers

## Create the Orders table

Run `create_table.py`.

Enable streams on the `orders` table.

## Create IAM Role

Create an IAM role with the following properties:

Trusted entity – Lambda  
Permissions – `AWSLambdaDynamoDBExecutionRole`, `AmazonSESFullAccess`  
Role name – `Lambda-OrderConfirmation-Role`

`AWSLambdaDynamoDBExecutionRole` provides list and read access to DynamoDB streams and write permissions to CloudWatch logs.

`AmazonSESFullAccess` allows sending email via SES.

## Create Lambda Function

Name - `OrderConfirmation`

Runtime - `Python 3.7`

Use the execution role created above.

Use `lambda_function.py` in this directory.

## Add the DynamoDB Trigger

DynamoDB table - `orders`

## Set `SENDER` Environment Variable

In the Lambda function set `SENDER` to an email address that has been verified in SES, if you are still in the sandbox. Otherwise, use an email address of your choice.
