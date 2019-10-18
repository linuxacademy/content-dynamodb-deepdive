# 6.2.1 - Write Sharding

## Create IAM Role

Create an IAM role with the following properties:

Trusted entity – Lambda  
Permissions – `AWSLambdaDynamoDBExecutionRole`, `AmazonDynamoDBFullAccess`  
Role name – `Lambda-AggregateVotes-Role`

## Create Lambda Function

Name - `AggregateVotes`

Runtime - `Python 3.7`

Use the execution role created above.

Use `lambda_function.py` in this directory.
