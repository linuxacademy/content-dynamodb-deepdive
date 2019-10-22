# 6.3.1 - Static Data Dumps

## Create S3 Bucket

Follow [these instructions](https://docs.aws.amazon.com/en_pv/AmazonS3/latest/dev/HostingWebsiteOnS3Setup.html) for creating an S3 bucket and configuring it as a website.

Be sure to apply the [bucket policy](bucket_policy.json), replacing `example-bucket` with the name of your bucket.

## Create IAM Role

Create an IAM role with the following properties:

- Trusted entity – Lambda  
- Permissions – `AWSLambdaDynamoDBExecutionRole`, `AmazonDynamoDBFullAccess`, `AmazonS3FullAccess`
- Role name – `Lambda-OrderLeaderboard-Role`

## Enable Streams

Enable streams on the `orders` table, selecting either "New image" or "New and old images".

## Create Lambda Function

- Name - `OrderLeaderboard`
- Runtime - `Python 3.7`
- Use the execution role created above.
- Use `lambda_function.py` in this directory.
- Set the `BUCKET` environment variable to the name of the bucket you created to host your static website.
- Create a DynamoDB trigger for the `orders` table

## Place Orders

Run `orders.py` and observe the `orders_leaderboard` update with album totals.

The S3 bucket will be updated with `index.html` containing the latest sales data.

Browse to `http://<bucket-name>.s3-website-us-east-1.amazonaws.com/` (assuming your bucket is in `us-east-1`).
