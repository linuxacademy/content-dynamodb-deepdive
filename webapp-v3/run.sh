#!/bin/sh

set -a
[ -f ./webapp/.env ] && . ./webapp/.env
set +a

FLASK_APP=webapp FLASK_ENV=development FLASK_DEBUG=1 flask run --host=0.0.0.0 --cert=adhoc

# Generate self-signed cert (required for OAuth2 callback)
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
# FLASK_APP=webapp FLASK_ENV=development FLASK_DEBUG=1 flask run --host=0.0.0.0 --cert=cert.pem --key=key.pem
