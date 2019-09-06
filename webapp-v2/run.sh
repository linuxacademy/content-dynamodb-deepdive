#!/bin/sh

S3_PREFIX='https://ddb-deep-dive-dev.s3-us-west-2.amazonaws.com/'

S3_PREFIX=$S3_PREFIX FLASK_APP=webapp FLASK_ENV=development FLASK_DEBUG=1 flask run --host=0.0.0.0
