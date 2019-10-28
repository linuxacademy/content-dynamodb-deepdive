#!/usr/bin/python3

import argparse, csv
import boto3
from time import sleep, time

def convertCSV(fileName):
    tableData = []

    rawData = open(fileName)
    tableList = rawData.readlines()
    rawData.close()

    '''
    ...
    "ԡ12ԡԘԡGiant Sandԡ",
    ...
    '''

    totalRows = len(tableList) -1
    csvData = csv.DictReader(tableList, delimiter = 'Ԙ', quotechar = 'ԡ')

    for row in csvData:
        if None in row.keys():
            continue
        else:    
            tableData.append(dict(row))

    '''
    ...
    {
        'id': '12',
        'name': 'Giant Sand'
    },
    ...
    '''

    for item in tableData:
        keysToDel = []
        
        for key, value in item.items():
            if value in {'Null', 'NULL', None, ''}:
                keysToDel.append(key)
            else:
                if '.' in value:
                    try:
                        value = float(value)
                        item[key] = {'N': str(value)}
                    except ValueError:
                        item[key] = {'S': str(value)}
                else:
                    try:
                        value = int(value)
                        item[key] = {'N': str(value)}
                    except ValueError:
                        item[key] = {'S': str(value)}

        for key in keysToDel:
            del item[key]
        
        '''
        ...
        {
            'id': {
                'N': '12'
            },
            'name': {
                'S': 'Giant Sand'
            }
        },
        ...
        '''

    return (tableData, totalRows)

def dynamoDBCreateTable(tableName):
    ddbClient = boto3.client('dynamodb')

    if tableName in ddbClient.list_tables()['TableNames']:
        return f"{tableName} already exists... TIME TO DO SOME CLOBBERING!"

    if tableName == 'user':
        tableAttributes = [{'AttributeName': 'email','AttributeType':'S'}]
        tableSchema = [{'AttributeName': 'email', 'KeyType': 'HASH'}]
    else:
        tableAttributes = [{'AttributeName': 'id','AttributeType':'N'}]
        tableSchema = [{'AttributeName': 'id', 'KeyType': 'HASH'}]
    
    print(f'Creating table: {tableName}')

    try:
        ddbClient.create_table(
            AttributeDefinitions = tableAttributes,
            KeySchema = tableSchema,
            BillingMode = 'PAY_PER_REQUEST',
            TableName = tableName
        )

        while ddbClient.describe_table(TableName=tableName)['Table']['TableStatus'] == 'CREATING':
            print(f'Waiting for {tableName} to be available...')
            sleep(3)

    except Exception as e:
        return e

    ddbClient = None
    return f'Succesfully created {tableName}'

def dynamoDBWriter(tableName, data):
    ddbClient = boto3.client('dynamodb')
    itemsCount = len(data)
    unprocessableItems = []

    for i in range(len(data)):
        data[i] = { "PutRequest": { "Item": data[i]}}

        '''
        --- data[i] ---
        {
            "PutRequest": {
                "Item": {
                    'id': {
                        'N': '12' 
                    },
                    'name': {
                        'S': 'Giant Sand'
                    }
                }
            }
        }
        '''

    # dataBatches = [ data[i * 25:(i +1) * 25] for i in range((len(data) + 25 -1) // 25) ]
    dataBatches = []
    for i in range((len(data) + 25 -1) // 25):
        dataBatches.append( data[i * 25:(i +1) * 25] )

    '''
    --- dataBatches ---
    [[{"PutRequest":...}, ...x25 ], [{"PutRequest":...}, ...x25 ]...]
    '''
    
    for batch in dataBatches:
        '''
        --- batch ---
        [{"PutRequest":...}, ...x25 ]
        '''
        try:
            response = ddbClient.batch_write_item(
                RequestItems={
                        tableName: batch
                    },
            )
        except Exception as e:
            return f'{e}\n {batch}'

        if len(response['UnprocessedItems']) > 0:
            batchCalls = 0
            unprocessed = True
            while unprocessed:
                batchCalls += 1

                if batchCalls > 3:
                    print(f'[!]: Unprocessed Items attempt - {batchCalls}\n{response["UnprocessedItems"]}')
                
                timeout = 2 ** batchCalls
                
                if timeout > 300:
                    itemsCount -= len(response['UnprocessedItems'][tableName])
                    unprocessableItems += response['UnprocessedItems'][tableName]
                    break
                
                sleep(timeout)
                try:
                    response = ddbClient.batch_write_item(RequestItems=response["UnprocessedItems"])
                except Exception as e:
                    print(e)

                if len(response['UnprocessedItems']) == 0:
                    unprocessed = False
    
    dataBatches = None
    return (itemsCount, unprocessableItems)

def main():
    startTime = int(time())
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required = True, help = "Csv File(s) to convert to JSON objects and put in DynamoDB table")
    args = vars(ap.parse_args())

    filesRaw = args['file']
    files = filesRaw.split(',')
    # ['album.csv', ' artist.csv', ' track.csv']

    fileNames = []
    for f in files:    
        fileNames.append(f.strip())
    # ['album.csv', 'artist.csv', 'track.csv']

    for fileName in fileNames:
        tableName = fileName.split('.')[0]
        
        print(dynamoDBCreateTable(tableName))

        dataToLoad = convertCSV(fileName)
        loadResults = dynamoDBWriter(tableName, dataToLoad[0])       

        if isinstance(loadResults, tuple):
            print(f'Loaded {loadResults[0]} items into {tableName} from {fileName} which contains {dataToLoad[1]} items')
            if len(loadResults[1]) > 0:
                print('The following items could not be processed:')
                for item in (loadResults[1]):
                    print(item)
        else:
            print(f'An error has occured:\n{loadResults}')
    
    endTime = int(time())
    totalSeconds = endTime - startTime
    totalMinutes = totalSeconds // 60
    remainingSeconds = totalSeconds % 60

    print(f'Loading all files took {totalMinutes} Minutes {remainingSeconds} Seconds')

if __name__ == '__main__':
    main()