# 6.6.1 - EMR

## Create EMR cluster

Select **two** `m5.xlarge` nodes or similar. Anything small such as `m1.medium` will lack sufficient resources.

The EMR cluster nodes all should have EC2 instance profile `EMR_EC2_DefaultRole` by default which has the policy `AmazonElasticMapReduceforEC2Role` attached. This policy grants both `dynamodb:*` and `s3:*` permissions.

## Connect to Master Node Using SSH

Ensure your master node's security group configuration allows SSH (22/tcp) inbound.

SSH using the following command:

`ssh -i <your-key-name>.pem hadoop@<master-public-dns>`

Where `your-key-name` is the keypair you specified when you created the EMR cluster, and `master-public-dns` is the **Master public DNS** name from the cluster summary page in the AWS management console.

At the command prompt for the current master node, type `hive`.

You should see the hive prompt after several seconds: `hive>`

## Create Hive Table

```sql
-- DynamoDB table 'pinehead_records_s3'
CREATE EXTERNAL TABLE pinehead (
  type string,
  id bigint,
  album_art string,
  artist_id bigint,
  format string,
  name_title string,
  price double,
  sku string,
  year bigint,
  album_id bigint,
  number string,
  length bigint)
STORED BY 'org.apache.hadoop.hive.dynamodb.DynamoDBStorageHandler' 
TBLPROPERTIES ("dynamodb.table.name" = "pinehead_records_s3",
"dynamodb.column.mapping" = "type:type,id:id,album_art:album_art,artist_id:artist_id,format:format,name_title:name_title,price:price,sku:sku,year:year,album_id:album_id,number:number,length:length");
```

## Query Data using SQL

**Example:** Find all albums by The Beatles sorted by year:

```sql
SELECT name_title, year 
FROM   pinehead 
WHERE  type = 'album' 
       AND artist_id = 303 
GROUP  BY name_title, year 
ORDER  BY year DESC;
```

To perform this same query with DynamoDB, everything after the `WHERE` clause requires post-return computation.

## Join DynamoDB Table With CSV File in S3

```sql
-- Loads orders.csv from S3 bucket, skipping header row
CREATE EXTERNAL TABLE Orders_S3(customer_id bigint, album_id bigint)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
LOCATION 's3://dynamodb-deep-dive-static-data-dump/orders/'
TBLPROPERTIES ("skip.header.line.count"="1");

SELECT o.customer_id, p.name_title, p2.name_title 
FROM Orders_S3 o
JOIN pinehead p ON o.album_id=p.id 
JOIN pinehead p2 ON p.artist_id = p2.id
WHERE p.type = 'album'
AND p2.type = 'artist';
```