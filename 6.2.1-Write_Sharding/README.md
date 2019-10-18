# 6.2.1 - Write Sharding

## Create IAM Role

Create an IAM role with the following properties:

Trusted entity – Lambda
Permissions – `AWSLambdaDynamoDBExecutionRole`, `AmazonDynamoDBFullAccess`
Role name – `lambda-dynamodb-write-sharding-role`

