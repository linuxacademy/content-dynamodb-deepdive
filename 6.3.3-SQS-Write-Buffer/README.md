# 6.3.3 - SQS Write Buffer

# Triggering Lambda from SQS

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

## Sending Messages to SQS

Run the provided script `orders.py` to send messages to SQS

**Example**: Send a message containing a random order to the `orders` queue every 0.1 second (10 messages per second):

`./orders.py -q orders -i 0.1`

Press `Ctrl+C` to quit.
