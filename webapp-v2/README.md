# Pinehead Records webapp v2

This version features:

- Some optimizations
- Better table structure (single hierarchical table)
- Local and Global secondary indexes
- Accounts in DynamoDB

## To create the v2 data model in your own account

```sh
aws configure set default.region us-east-1
pip3 install --user boto3
curl https://raw.githubusercontent.com/linuxacademy/content-dynamodb-deepdive/master/labs/bootstrap/tablebootstrap.py | python3 /dev/stdin -s 2 -f s3://dynamodblabs/pinehead_records_s2.csv
```
