#!/bin/sh

S3_PREFIX='https://dynamodbdeepdive.s3.amazonaws.com/'

S3_PREFIX=$S3_PREFIX FLASK_APP=webapp FLASK_ENV=development FLASK_DEBUG=1 flask run --host=0.0.0.0
