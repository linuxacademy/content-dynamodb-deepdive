# 6.2.2 - Aggregation with Streams

## Create IAM Role

Create an IAM role with the following properties:

Trusted entity – Lambda  
Permissions – `AWSLambdaDynamoDBExecutionRole`, `AmazonDynamoDBFullAccess`  
Role name – `Lambda-AggregateVotesStreams-Role`

## Create Lambda Function

Name - `AggregateVotesStreams`

Runtime - `Python 3.7`

Use the execution role created above.

Use `lambda_function.py` in this directory.
