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

Role name: `Lambda-ddb2es-Role`

Use policy in `lambda-role.json` with `Lambda` as the trusted entity.

## Package up the Lambda Function

```sh
cd content-dynamodb-deepdive/6.6.2-Elasticsearch/ddb2es
pip3 install requests -t .
pip3 install requests_aws4auth -t .
zip -r ../ddb2es.zip *
```

## Create Lambda Function

Name: `ddb2es`  
Runtime: Python 3.7  
Function code: Upload the `ddb2es.zip` file created in the previous step.  
Execution role: Use the role `Lambda-ddb2es-Role` created in the previous step.  

- Configure basic settings for 1024 MB memory and 30 sec timeout.

- Configure the Lambda function for your VPC.
  - Select all subnets. 
  - Ensure you select a security group with outbound access to `0.0.0.0/0` for all ports.

## Configure the DynamoDB Trigger

- Table: `pinehead_records_s3`
- Batch size: 1000 (this is the maximum)
- Starting position: Trim horizon

**Trim horizon** will start reading at the oldest record in the shard.

## Import Data into DynamoDB

This will create the v3 data model in your account (the `-c` or `--clean` flag will delete the existing table, if specified):

Make sure you use have at least 10 GB free memory for the bootstrap script to run without errors. This runs most quickly on an EC2 instance in the same region as the target DynamoDB table.

```sh
aws configure set default.region us-east-1
sudo yum install python3 -y
pip3 install --user boto3
curl https://raw.githubusercontent.com/linuxacademy/content-dynamodb-deepdive/master/labs/bootstrap/tablebootstrap.py | python3 /dev/stdin -s 3 -f s3://dynamodblabs/artist.csv,s3://dynamodblabs/album.csv,s3://dynamodblabs/track.csv
```

## Query Elasticsearch

You may create an SSH tunnel to simulate a local install of Elasticsearch:

<!--
ssh -i ~/aws/aws-cloudshare.pem ec2-user@3.231.202.192 -N -L 9200:vpc-pinehead-nbtscv4abalj7nmsikj4bwaztm.us-east-1.es.amazonaws.com:443
-->

```sh
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-instance-public-ip -N -L 9200:vpc-your-amazon-es-domain.region.es.amazonaws.com:443
```

Navigate to <https://localhost:9200/_plugin/kibana/> in your web browser. You might need to acknowledge a security exception.

### Create Index Pattern

1. Define an index pattern of `*` will match the `lambda-index` index. Select **Next Step**.

2. Select **I don't want to use the Time Filter**.

3. Select **Create index pattern**.

### Visualize

The **Visualize / Create** screen will show you the `Count` metric, indicating the number of items in the index. This value should continue to grow until the Lambda function has processes the entire DynamoDB stream. You can change this to `Unique Count` on the `_id` field.

### Discover

Search using [KQL](https://www.elastic.co/guide/en/kibana/current/kuery-query.html) syntax. For example, a partial match on track name containing the string `Intro`:

```text
type.S:track and name_title.S:Intro
```
