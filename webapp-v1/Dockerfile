FROM python:3.7
LABEL maintainer="Mark Richman <mark@linuxacademy.com>"

RUN pip3 install pipenv

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN set -ex && pipenv install --deploy --system

COPY . .

EXPOSE 5000

CMD [ "gunicorn", "-b0.0.0.0:5000", "webapp:app" ]