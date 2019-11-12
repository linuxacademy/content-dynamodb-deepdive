#!/bin/sh

set -a
[ -f ./webapp/.env ] && . ./webapp/.env
set +a

FLASK_APP=webapp FLASK_ENV=development FLASK_DEBUG=1 flask run --host=0.0.0.0
