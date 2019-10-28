# 6.3.3 - SQS Write Buffer

## Create DynamoDB Table

```sh
aws dynamodb create-table --table-name orders \
  --attribute-definitions AttributeName=id,AttributeType=S \
                          AttributeName=timestamp,AttributeType=N \
  --key-schema AttributeName=id,KeyType=HASH \
               AttributeName=timestamp,KeyType=RANGE \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
```

**Note:** We deliberately set RCU/WCU=1 to induce throttling. If your `orders` table already exists, you must change the provisioned throughput to match the above.

## Create SQS Queue

```sh
aws sqs create-queue --queue-name orders
```

## Create IAM Execution Role for Lambda

- Use the `lambda_execution_role.json` to create an IAM policy `Lambda-SQSWriteBuffer-Policy`.
- Edit the policy to reflect your AWS account id.
- Attach this policy to a new IAM role `Lambda-SQSWriteBuffer-Role`.

## Create Lambda Function

Create a new Python 3.7 function named `SQSWriteBuffer` with the execution role `Lambda-SQSWriteBuffer-Role`.

- Set the environment variable `QUEUE_NAME` to `orders`.
- Set the environment variable `DYNAMODB_TABLE` to `orders`.
- Ensure the function timeout is less than the queue's visibility timeout (i.e. set function timeout = 15 sec)
- Add a trigger for SQS specifying the `orders` queue.
- Wait up to 1 min for the trigger to create in the **Enabled** state.

## Sending Messages to SQS

Run the provided script `orders.py` to send messages to SQS

**Example**: Send a message containing a random order to the `orders` queue every 0.1 second (10 messages per second):

```sh
cd content-dynamodb-deepdive/6.3.3-SQS-Write-Buffer
pipenv install
pipenv shell
./orders.py -q orders -i 0.1`
```

Press `Ctrl+C` to quit.

## Review

Review the CloudWatch logs for the Lambda function. You may see messages that read:

> ProvisionedThroughputExceededException: The level of configured provisioned throughput for the table was exceeded. Consider increasing your provisioning level with the UpdateTable API.

This indicates that your messages are being throttled.

After some time, observe that the orders have been inserted into the `orders` table. Also observe that the SQS queue is empty.

