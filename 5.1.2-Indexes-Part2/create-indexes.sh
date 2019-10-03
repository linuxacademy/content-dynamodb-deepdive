#!/bin/sh

# The following queries from our application inform our indexes:
# Album.get_by_artist_id(artist_id)
# Album.find_by_artist(artist_name)
# Album.find_by_artist_ids(artist_ids)
# Album.find_by_title()
# Album.find_by_track()
# Artist.find_by_name()
# Track.get_by_album_id()

# Album table

aws dynamodb update-table \
  --table-name album \
  --global-secondary-indexes IndexName=artist_id-index,\
    KeySchema=["{AttributeName=artist_id,KeyType=HASH}"] \
  --billing-mode=PAY_PER_REQUEST

aws dynamodb update-table \
  --table-name album \
  --global-secondary-indexes IndexName=artist_name-index,\
    KeySchema=["{AttributeName=artist_name,KeyType=HASH}"] \
  --billing-mode=PAY_PER_REQUEST

aws dynamodb update-table \
  --table-name album \
  --global-secondary-indexes IndexName=artist_title-index,\
    KeySchema=["{AttributeName=artist_title,KeyType=HASH}"] \
  --billing-mode=PAY_PER_REQUEST

aws dynamodb update-table \
  --table-name album \
  --global-secondary-indexes IndexName=artist_track-index,\
    KeySchema=["{AttributeName=artist_track,KeyType=HASH}"] \
  --billing-mode=PAY_PER_REQUEST

# Artist table

aws dynamodb update-table \
  --table-name artist \
  --global-secondary-indexes IndexName=name-index,\
    KeySchema=["{AttributeName=name,KeyType=HASH}"] \
  --billing-mode=PAY_PER_REQUEST

# Track table

aws dynamodb update-table \
  --table-name track \
  --global-secondary-indexes IndexName=album_id-index,\
    KeySchema=["{AttributeName=album_id,KeyType=HASH}"] \
  --billing-mode=PAY_PER_REQUEST