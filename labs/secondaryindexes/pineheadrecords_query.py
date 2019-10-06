#!/usr/bin/python3

import boto3
from time import time

def listTables():
    ddbClient = boto3.client('dynamodb')
    try:
        tables = ddbClient.list_tables()['TableNames']
    except Exception as e:
        print(e)
        return ''
    
    return tables


def query(tableName, attributes):
    # attributes = { 'artist_id': '20211', }
    ddbClient = boto3.client('dynamodb')
    tableInfo = ddbClient.describe_table(TableName=tableName)['Table']

    startTime = time()
    if tableName == 'album':
        totalCapacity = 0
        totalCount = 0
        totalScanned = 0

        if  'title' in attributes.keys():
            try:
                queryResponse = ddbClient.scan(
                    TableName = tableName,
                    ExpressionAttributeValues = {
                        ':tk': {
                            'S': attributes['title']
                        }
                    },
                    ExpressionAttributeNames = {
                        '#Tk': 'title'
                    },
                    FilterExpression = '#Tk = :tk',
                    ReturnConsumedCapacity = 'TOTAL'
                )
            except Exception as e:
                return e

            totalCapacity += queryResponse["ConsumedCapacity"]["CapacityUnits"]
            totalCount += queryResponse["Count"]
            totalScanned += queryResponse["ScannedCount"]

            while 'LastEvaluatedKey' in queryResponse.keys():
                try:
                    queryResponse = ddbClient.scan(
                        TableName = tableName,
                        ExpressionAttributeValues = {
                            ':tk': {
                                'S': attributes['title']
                            }
                        },
                        ExpressionAttributeNames = {
                            '#Tk': 'title'
                        },
                        FilterExpression = '#Tk = :tk',
                        ReturnConsumedCapacity = 'TOTAL',
                        ExclusiveStartKey = queryResponse['LastEvaluatedKey']
                    )
                except Exception as e:
                    return e

                totalCapacity += queryResponse["ConsumedCapacity"]["CapacityUnits"]
                totalCount += queryResponse["Count"]
                totalScanned += queryResponse["ScannedCount"]

            queryResponse["ConsumedCapacity"]["CapacityUnits"] = totalCapacity
            queryResponse["Count"] = totalCount
            queryResponse["ScannedCount"] = totalScanned

        elif 'artist_id' in attributes.keys():
            try:
                queryResponse = ddbClient.scan(
                    TableName = tableName,
                    ExpressionAttributeValues = {
                        ':ak': {
                            'N': attributes['artist_id']
                        },
                        ':fk': {
                            'S': attributes['format']
                        }
                    },
                    ExpressionAttributeNames = {
                        '#Ak': 'artist_id',
                        '#Fk': 'format'
                    },
                    FilterExpression = '#Ak = :ak and #Fk = :fk',
                    ReturnConsumedCapacity = 'TOTAL'
                )
            except Exception as e:
                return e

            totalCapacity += queryResponse["ConsumedCapacity"]["CapacityUnits"]
            totalCount += queryResponse["Count"]
            totalScanned += queryResponse["ScannedCount"]

            while 'LastEvaluatedKey' in queryResponse.keys():
                try:
                    queryResponse = ddbClient.scan(
                        TableName = tableName,
                        ExpressionAttributeValues = {
                            ':ak': {
                                'N': attributes['artist_id']
                            },
                            ':fk': {
                                'S': attributes['format']
                            }
                        },
                        ExpressionAttributeNames = {
                            '#Ak': 'artist_id',
                            '#Fk': 'format'
                        },
                        FilterExpression = '#Ak = :ak AND #Fk = :fk',
                        ReturnConsumedCapacity = 'TOTAL',
                        ExclusiveStartKey = queryResponse['LastEvaluatedKey']
                    )
                except Exception as e:
                    return e

                totalCapacity += queryResponse["ConsumedCapacity"]["CapacityUnits"]
                totalCount += queryResponse["Count"]
                totalScanned += queryResponse["ScannedCount"]
            
            queryResponse["ConsumedCapacity"]["CapacityUnits"] = totalCapacity
            queryResponse["Count"] = totalCount
            queryResponse["ScannedCount"] = totalScanned
        else:
            return f'Invalid attributes\nAttributes: {attributes}'
        

    elif tableName == 'album_indexed':
        if 'LocalSecondaryIndexes' not in tableInfo.keys() and 'GlobalSecondaryIndexes' not in tableInfo.keys():
            return 'Table not completely formed, please ensure all Local and Global secondary indexes have been added'

        if 'artist_id' in attributes.keys():
            for index in tableInfo['LocalSecondaryIndexes']:
                for att in index['KeySchema']:
                    if att['AttributeName'] == 'format':
                        try:
                            queryResponse = ddbClient.query(
                                TableName = tableName,
                                IndexName = index['IndexName'],
                                ReturnConsumedCapacity = 'TOTAL',
                                ExpressionAttributeValues = {
                                    ':pk': {
                                        'N': attributes['artist_id'],
                                    },
                                    ':ik': {
                                        'S': attributes['format'],
                                    },
                                },
                                ExpressionAttributeNames = {
                                    '#Ak': 'artist_id',
                                    '#Fk': 'format'
                                },
                                KeyConditionExpression = '#Ak = :pk AND #Fk = :ik'
                            )
                        except Exception as e:
                            return e
                
        elif 'title' in attributes.keys():
            for index in tableInfo['GlobalSecondaryIndexes']:
                for att in index['KeySchema']:
                    if att['AttributeName'] == 'title':
                        try:
                            queryResponse = ddbClient.query(
                                TableName = tableName,
                                IndexName = index['IndexName'],
                                ReturnConsumedCapacity = 'TOTAL',
                                ExpressionAttributeValues={
                                    ':ik': {
                                        'S': attributes['title']
                                    }
                                },
                                ExpressionAttributeNames = {
                                    '#Tk': 'title'
                                },
                                KeyConditionExpression = '#Tk = :ik'
                            )
                        except Exception as e:
                            return e

        else:
            return f'Invalid attributes provided\nAttributes: {attributes}'
    else:
        return f'Invalid table name provided\nTable Name: {tableName}'


    opTime = {'seconds': 0}
    endTime = time()
    opTime['seconds'] = endTime - startTime
    if opTime['seconds'] > 60:
        opTime['minutes'] = opTime['seconds'] // 60
        opTime['seconds'] = opTime['seconds'] % 60

    if 'minutes' in opTime.keys():
        return f'Query/Scan complete in {opTime["minutes"]} Minutes {opTime["seconds"]} Seconds\nItems returned: {queryResponse["Count"]} of Items Scanned: {queryResponse["ScannedCount"]}\nRead Capacity Consumed: {queryResponse["ConsumedCapacity"]["CapacityUnits"]} Capacity Units'
    else:
        return f'Query/Scan complete in {int(opTime["seconds"] * 1000)} Milliseconds\nItems returned: {queryResponse["Count"]} of Items Scanned: {queryResponse["ScannedCount"]}\nRead Capacity Consumed: {queryResponse["ConsumedCapacity"]["CapacityUnits"]} Capacity Units'

def main():
    attributesToTest = [
        {
            'artist_id': '251',
            'format': '12" Vinyl'
        },
        {
            'title': 'Rio'
        }
    ]
    
    for attributes in attributesToTest:
        print('\nTesting Scan/Query with attributes:')
        for key, value in attributes.items():
            print(f'Key: {key}, Value: {value}')
        if 'album_indexed' in listTables():
            print('Scan:')
            print(query('album', attributes))
            print('Query:')
            print(query('album_indexed', attributes))
        else:
            print('Scan:')
            print(query('album', attributes))
            print('Please create the album_indexed table!')

if __name__ == '__main__':
    main()