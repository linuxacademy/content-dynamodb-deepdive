# 6.6.2 - Elasticsearch

## Create Elasticsearch Domain

**Elasticsearch domain name** can be anything you like; this is not an internet domain name.

Enable a security group with ports 22/tcp and 443/tcp open inbound.

Domain initialization takes about 10 minutes. You cannot load data or run queries against your domain until the initialization is complete. The domain status will change to Active as soon as your domain is ready to use.

## Create the DynamoDB Table

- Table: `pinehead_records_s3`
- PK: type (String)
- SK: id (Number)
- On-demand capacity mode

Enable streams for "New and old images"

## Create IAM Execution Role for Lambda Function

Use policy in `lambda-role.json` with `Lambda` as the trusted entity.

## Package up the Lambda Function

```sh
cd ddb2es
pip install requests -t .
pip install requests_aws4auth -t .
zip -r ../ddb2es.zip *
```

## Create Lambda Function

Name: `ddb2es`
Runtime: Python 3.7
Function code: Upload the `ddb2es.zip` file created in the previous step.
Execution role: Use the role created in the previous step.

## Configure the DynamoDB Trigger

- Table: `pinehead_records_s3`
- Batch size: 100
- Starting position: Trim horizon

**Trim horizon** will start reading at the oldest record in the shard.

## Import Data into DynamoDB

This will create the v3 data model in your account (the `-c False` flag will prevent the existing table from being overwritten):

```sh
aws configure set default.region us-east-1
pip3 install --user boto3
curl https://raw.githubusercontent.com/linuxacademy/content-dynamodb-deepdive/master/labs/bootstrap/tablebootstrap.py | python3 /dev/stdin -c False -s 3 -f s3://dynamodblabs/pinehead_records_s3.csv
```

## Query Elasticsearch

You may create an SSH tunnel to simulate a local install of Elasticsearch:

```sh
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-instance-public-ip -N -L 9200:vpc-your-amazon-es-domain.region.es.amazonaws.com:443
```

Navigate to <https://localhost:9200/_plugin/kibana/> in your web browser. You might need to acknowledge a security exception.
