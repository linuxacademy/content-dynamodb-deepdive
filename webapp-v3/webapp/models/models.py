from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

import boto3
from boto3.dynamodb.conditions import Key
from flask_login import UserMixin

user_table = boto3.resource("dynamodb").Table("user")


@dataclass
class Track:
    id: int
    name: str
    length: int
    number: str


@dataclass
class Album:
    id: int
    sku: str
    artist_id: int
    title: str
    year: int
    format: str
    price: float
    cover_art: str = None
    artist: Artist = None
    tracks: List[Track] = field(default_factory=list)

    @property
    def album_art(self):
        id_album = list(str(self.id))
        id_album.reverse()
        filepath = "/".join(id_album)
        s3_uri = f"{os.environ['S3_PREFIX']}albumart/{filepath}/{self.id}.jpg"
        print(s3_uri)
        return s3_uri


@dataclass
class Artist:
    id: int
    name: str
    albums: List[Album]


class User(UserMixin):
    def __init__(self, email, password):
        self._email = email
        self._password = password

    @property
    def id(self):
        return self._email

    @property
    def email(self):
        return self._email

    @property
    def password(self):
        return self._password

    @staticmethod
    def get_user(email):
        print("email", email)
        response = user_table.query(KeyConditionExpression=Key("email").eq(email))
        items = response.get("Items")

        if items is None:
            return None

        if not items:
            return None

        u = User(items[0]["email"], items[0]["password"])
        return u

    def __repr__(self):
        return f"User('{self._email}')"

    def add(self):
        """saves a new record to DynamoDB"""
        user_table.put_item(Item={"email": self.email, "password": self.password})

    def update(self):
        """updates an existing record in DynamoDB"""
        user_table.update_item(
            Key={"email": self.email},
            UpdateExpression="SET password=:password",
            ExpressionAttributeValues={":password": self.password},
        )
