# 6.3.2 - DAX

## Create cluster

- Cluster name: `pinehead`
- Node type: `dax.t2.small`
- Cluster size: `3 nodes`
- Encryption: `Enable encryption` (optional)
- IAM Service role for DynamoDB access: `Create new`
- IAM role name: `DAXtoDynamoDB`
- IAM role policy: `Read only`
- IAM policy name: `DAXtoDynamoDBPolicy`
- Target DynamoDB table: `pinehead_records_s2`
- Subnet group: `Create new`
- Name: `dax-subnet-group`
- VPC ID: Your choice
- Subnets: All
- Security group: Select an SG which allows 8111/tcp inbound
- Cluster settings: Use default settings
- Click **Launch cluster**

Launching a cluster may take several minutes. Note the cluster's **endpoint URL**. You will use this in your code.

## Benchmarking DAX

Run `pipenv install` and `pipenv shell` to configure a virtualenv with dependencies.

Alternatively, run `pip3 install --user amazon-dax-client boto3`.

### Without DAX

```sh
./dax.py -t pinehead_records_s2 -k Surrounded
```

### With DAX

```sh
./dax.py -t pinehead_records_s2 -k Surrounded -e your-endpoint-here.clustercfg.dax.use1.cache.amazonaws.com:8111
```
