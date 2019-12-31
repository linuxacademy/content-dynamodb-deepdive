# Pinehead Records v1 - Fundamental DynamoDB

- Naïve migration from CSV to DynamoDB
- 3 DDB tables mimicking the relational structure
- images are moved to S3 with URI in DDB attribute
- no indexes
- accounts in DB

## Deploying Schema v1 to DynamoDB

This script will create the required DynamoDB tables and populate the data using source data from S3:

```sh
curl https://raw.githubusercontent.com/linuxacademy/content-dynamodb-deepdive/master/labs/bootstrap/tablebootstrap.py | python3 /dev/stdin -s 1 -o csv -f s3://dynamodblabs/artist.csv,s3://dynamodblabs/album.csv,s3://dynamodblabs/track.csv
```

This can take some time to complete.

## Running the web application

If you are on Amazon Linux 2, you may need to install Git and Python 3:

```sh
sudo yum install git python3 -y
```

Make sure you have `pipenv` installed:

```sh
pip3 install --user pipenv
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
