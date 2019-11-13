# Pinehead Records Web App v3

This final version of the Pinehead Records web application features multiple GSIs, each informed by our various queries:

- `find_albums_by_artist_name()`
- `find_album_by_artist_and_title()`
- `find_albums_by_title()`
- `find_albums_by_track()`
- `find_albums_by_artist_id()`
- `get_tracks_by_album_id()`

Note that the `user` table is still separate from the `pinehead_records_s3` table.

## Table Info

| Name          | pinehead_records_s3 |
|---------------|---------------------|
| Partition Key | type (String)       |
| Sort Key      | id (Number)         |

## Indexes

| Type | Name                  | Partition Key       | Sort Key          | Attributes |
| -----|-----------------------|---------------------|-------------------|----------- |
| LSI  | type-name_title-index | type (String)       | name_title        | ALL        |
| GSI  | name_title-index      | name_title (String) | -                 | ALL        |
| GSI  | artist_id-type-index  | artist_id (Number)  | type (String)     | ALL        |
| GSI  | type-album_id-index   | type (String)       | album_id (Number) | ALL        |
 
## Setup

### Album Art S3 Bucket

Album art is hosted in an S3 bucket. You may use your own bucket, or the bucket provided for use with this course. In either case, copy `.env.example` to a new file named `.env` and set the bucket name.

For example:

```sh
export S3_PREFIX=https://dynamodbdeepdive.s3.amazonaws.com/`
```

Note that the trailing slash is significant.

### Create the `user` table

```sh
aws dynamodb create-table --cli-input-json file://create-table-user.json
```

### Import Data into DynamoDB

This will create the v3 data model in your account (the `-c` or `--clean` flag will delete the existing table, if specified):

Make sure you use have at least 10 GB free memory for the bootstrap script to run without errors. This runs most quickly on an EC2 instance in the same region as the target DynamoDB table.

Using Amazon Linux 2:

```sh
aws configure set default.region us-east-1
sudo yum install python3 -y
pip3 install --user boto3
curl https://raw.githubusercontent.com/linuxacademy/content-dynamodb-deepdive/master/labs/bootstrap/tablebootstrap.py | python3 /dev/stdin -s 3 -f s3://dynamodblabs/artist.csv,s3://dynamodblabs/album.csv,s3://dynamodblabs/track.csv
```

This can take some time to complete.

## Running the web application

Make sure you have `pipenv` installed.

```sh
pip3 install pipenv
```

### Create the virtual environment

```sh
pipenv install
pipenv shell
```

### Run the application

```sh
./run.sh
```

The application will be available on port 5000 by default.
