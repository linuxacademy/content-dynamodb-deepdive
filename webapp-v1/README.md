# Pinehead Records v1 - Fundamental DynamoDB

- Naïve migration from MySQL to DynamoDB
- 3 DDB tables mimicking the relational structure
- images are moved to S3 with URI in DDB attribute
- no indexes
- accounts in DB

## Setting up DynamoDB local

There are multiple ways to set up DynamoDB local. We will use the [downloadable Java version](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html):

```sh
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar
```

This will store a `.db` file in the current directory.

## Create the DynamoDB tables

If using DynamoDB local, append `--endpoint-url http://localhost:8000` to the following:

```sh
aws dynamodb create-table --cli-input-json file://create-table-artist.json
aws dynamodb create-table --cli-input-json file://create-table-album.json
aws dynamodb create-table --cli-input-json file://create-table-track.json
aws dynamodb create-table --cli-input-json file://create-table-user.json
aws dynamodb list-tables
```

## Running with Docker

Build:

`docker build -t pinehead .`

Run:

```sh
docker run -it -p 5000:5000 \
  -e S3_PREFIX='https://ddb-deep-dive-dev.s3-us-west-2.amazonaws.com/ \
  -e AWS_DEFAULT_REGION='us-east-1' \
  -e AWS_ACCESS_KEY_ID='AKIAxxxxxxxxxx' \
  -e AWS_SECRET_ACCESS_KEY='xxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
  mrichman/pinehead-records:v1
```

## Queries

```
- Home page
  - New Arrivals (or Releases): all albums sorted by year desc
- Search by artist name: returns artist name, id
- Search by album name: returns list of albums:
  - album id, artist_id, title, format, price, s3_uri, track list:
    - track id, name, length, position
- Search by track name: returns list of albums containing that track name:
  - album id, artist_id, title, format, price, s3_uri, track list:
    - track id, name, length, position
- Get `/artist/id`: returns list of albums
- Get `/album/id`: returns album + track list
- Login-related stuff I haven't thought about yet
  - username, email
```
