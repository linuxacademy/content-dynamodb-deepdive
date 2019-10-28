import argparse, random, csv
import boto3
from time import time, sleep
from sys import getsizeof
from multiprocessing import Pool, Manager, current_process, active_children

class csvUtil:
    def __init__(self, inputData):
        self.csvData = list(csv.reader(inputData, delimiter = 'Ԙ', quotechar = 'ԡ'))
    
    def convertToObj(self, outFormat):
        headings = self.csvData[0]
        items = []

        for i in range(len(self.csvData)):
            dataDict = {}
            if i > 0:
                for v in range(len(self.csvData[i])):
                    
                    if self.csvData[i][v] == 'Null' or self.csvData[i][v] == None:
                        continue
                    
                    value = self.csvData[i][v]

                    if v > len(headings):
                        index = len(headings) - 1
                    else:
                        index = v

                    try:
                        if '.' in value:
                            try:
                                dataDict[headings[index]] = float(value)
                            except ValueError:
                                dataDict[headings[index]] = value
                        else:
                            try:
                                dataDict[headings[index]] = int(value)
                            except ValueError:
                                dataDict[headings[index]] = value
                    except Exception:
                        pass

                if outFormat == 'dynamodb':
                    for key, value in dataDict.items():
                        if isinstance(value, int) or isinstance(value, float):
                            dataDict[key] = {'N': str(value)}
                        elif isinstance(value, str):
                            dataDict[key] = {'S': value}
                        else:
                            print('Error, invalid datatype!')
                            return
                    items.append(dataDict)
                elif outFormat == 'json':    
                    items.append(dataDict)
                else:
                    return "Invalid format option provided"
        
        return items

class s3:
    def __init__(self, bucketName):
        self.s3Client = boto3.client('s3')
        self.bucket = bucketName

    def getObject(self, objectKey):
        return self.s3Client.get_object(Bucket = self.bucket, Key = objectKey)['Body'].read().decode('utf-8').splitlines(True)
    
class DynamoDB:
    def __init__(self):
        self.client = boto3.client('dynamodb')
        self.table = boto3.resource('dynamodb')
        self.batchTrys = 0

    def listTables(self):
        return self.client.list_tables()['TableNames']

    def getTableStatus(self, tableName):
        return self.client.describe_table(TableName=tableName)['Table']['TableStatus']

    def deleteTable(self, tableName):
        self.client.delete_table(TableName=tableName)

        while tableName in self.listTables():
            if self.getTableStatus(tableName) == "DELETING":
                print(f'[!]: Table {tableName} - Deleting...')
                sleep(3)
        
        return

    def createTable(self, tableName, attributes, keySchema, billingMode, provisionedThroughput = {}, LSI = None, GSI = None ):
        print(f'[!]: Creating {tableName}')
            
        if tableName in self.listTables():
            print(f'[!]: Cleanup enabled, deleting existing table {tableName}')
            self.deleteTable(tableName)

        
        try:
            if billingMode == 'PROVISIONED':
                self.client.create_table(
                    AttributeDefinitions = attributes,
                    KeySchema = keySchema,
                    ProvisionedThroughput = provisionedThroughput,
                    TableName = tableName
                )
            elif billingMode == 'PAY_PER_REQUEST':
                try:
                    self.client.create_table(
                        AttributeDefinitions = attributes,
                        KeySchema = keySchema,
                        BillingMode = billingMode,
                        LocalSecondaryIndexes = LSI,
                        GlobalSecondaryIndexes = GSI,
                        TableName = tableName
                    )
                except Exception:
                    try:
                        self.client.create_table(
                            AttributeDefinitions = attributes,
                            KeySchema = keySchema,
                            BillingMode = billingMode,
                            LocalSecondaryIndexes = LSI,
                            TableName = tableName
                        )
                    except Exception:
                        try:
                            self.client.create_table(
                                AttributeDefinitions = attributes,
                                KeySchema = keySchema,
                                BillingMode = billingMode,
                                GlobalSecondaryIndexes = GSI,
                                TableName = tableName
                            )
                        except Exception:
                            try:
                                self.client.create_table(
                                    AttributeDefinitions = attributes,
                                    KeySchema = keySchema,
                                    BillingMode = billingMode,
                                    TableName = tableName
                                )
                            except Exception as e:
                                print(e)

        except Exception as e:
            return e
        
        while self.getTableStatus(tableName) == 'CREATING':
            print(f'[!]: Table {tableName} - Creating...')
            sleep(3)
        
        print(f'[+]: Table {tableName} created')
        return

    def batchWrite(self, table, items):
        if len(items) > 25:
            return "Error: Batch too large"

        try:
            response = self.client.batch_write_item(
                RequestItems={
                    table: items
                },
            )

            if len(response['UnprocessedItems']) > 0:
                if self.batchTrys > 3:
                    print(f'[!]: Unprocessed Items attempt - {self.batchTrys}')
                self.batchTrys += 1
                timeout = 2 ** self.batchTrys
                if timeout > 300:
                    raise Exception('Time limit exceeded for retries (300 seconds)')
                sleep(timeout)
                self.batchWrite(table, response['UnprocessedItems'][table])
            else:
                self.batchTrys = 0

            return response
        except Exception as e:
            print(f'[-]: Exception encountered tries {self.batchTrys}\n     {e}')
            return e

def worker(table, chunkStart, chunkEnd, status, data, schema3File):
    ddb = DynamoDB()
    procName = current_process().name

    dataToPut = [ data[i * 25:(i +1) * 25] for i in range((len(data) + 25 -1) // 25) ]

    for rowList in dataToPut:
        batchDataSize = 0
        items = []
        
        for row in rowList:
            putItem = {
                'PutRequest': {
                    'Item': {
                    }
                }
            }

            keysToDel = []
            if schema3File != None:
                if 'artist_name' in row.keys():
                    row['name_title'] = row['artist_name']
                    del row['artist_name']
                if 'name' in row.keys():
                    row['name_title'] = row['name']
                    del row['name']
                if 'title' in row.keys():
                    row['name_title'] = row['title']
                    del row['title']

            for k,v in row.items():
                batchDataSize += getsizeof(v)
                if v in {'Null', 'NULL', None, ''}:
                    keysToDel.append(k)
                elif k == 'artist_name':
                    row[k] = {'S': str(v)}
                elif k == 'name':
                    row[k] = {'S': str(v)}
                elif k == 'id':
                    row[k] = {'N': str(v)}
                elif k == 'format':
                    row[k] = {'S': str(v)}
                elif k == 'price':
                    row[k] = {'N': str(v)}
                elif k == 'title':
                    row[k] = {'S': str(v)}
                elif k == 'year':
                    row[k] = {'N': str(v)}
                elif k == 'track_information':
                    row[k] = {'S': str(v)}
                elif k == 'name_title':
                    row[k] = {'S': str(v)}
                else:
                    if '.' in str(v):
                        try:
                            v = float(v)
                            row[k] = {'N': str(v)}
                        except ValueError:
                            row[k] = {'S': str(v)}
                    else:
                        try:
                            v = int(v)
                            row[k] = {'N': str(v)}
                        except ValueError:
                            row[k] = {'S': str(v)}

            if schema3File != None:
                row['type'] = {'S': str(schema3File)}

            for key in keysToDel:
                del row[key]

            for k,v in row.items():    
                    putItem['PutRequest']['Item'][k] = v

            if table in {'album', 'pinehead_records_s2', 'pinehead_records_s3'}:
                album_id = str(row['id']['N'])
                id_album = list(album_id)
                id_album.reverse()
                filepath = '/'.join(id_album)
                filename = f'{album_id}.jpg'
                fullpath = f'/albumart/{filepath}/{filename}'

                putItem['PutRequest']['Item']['album_art'] = {
                    'S' : fullpath
                }
        
            items.append(putItem)

        if batchDataSize // 1000 > 1000:
            splitItems = [items[i * 5:(i + 1) * 5] for i in range((len(items) + 5 - 1) // 5 )]

            for i in splitItems:
                try:
                    ddb.batchWrite(table, i)
                except Exception as e:
                    print(f'[-]: {procName} Exception encountered - {e}')
                    print(row)
            
        else:
            try:
                ddb.batchWrite(table, items)
            except Exception as e:
                print(f'[-]: {procName} Exception encountered - {e}')
                print(row)
        if schema3File != None:
            status[schema3File] += 25
        else:
            status[table] += 25

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--processes', type = int, default = 10, help = "Number of processes to use")
    ap.add_argument('-s', '--schema', required = True, choices = ['1', '2', '3'], help = 'Schema to migrate to (1, 2 or 3)')
    ap.add_argument('-c', '--clean', action = 'store_false', help = 'Specify if existing tables should be deleted')
    ap.add_argument('-f', '--file', help = 'Location of csv file(s) if source is csv')
    args = vars(ap.parse_args())

    workerProcesses = args['processes']
    processPool = Pool(processes = workerProcesses)
    schema = args['schema']
    clean = args['clean']
    print(f'Clean status: {clean}')
    tableArgs = []

    fileLocations = args['file']
    if fileLocations == None:
        print('File location must be provided when using the data origin is csv')
        return
    
    ddb = DynamoDB()
    status = Manager().dict()
    fileLocations = fileLocations.split(',')
    csvData = {}

    for fileName in fileLocations:
        if fileName[:3] == 's3:':
            bucketName = fileName.split('://')[1].split('/')[0]
            dataBucket = s3(bucketName)
            s3Key = fileName.split('://')[1].split('/')[1]
            s3Data = dataBucket.getObject(s3Key)
            csvFile = csvUtil(s3Data)
            csvData[fileName.split('/')[-1].split('.')[0]] = csvFile.convertToObj('json')
        else:
            csvFile = csvUtil(open(fileName))

            if fileName[0] == '/':
                fileKey = fileName.split('/')[-1].split('.')[0]
            else:
                fileKey = fileName.split('.')[0]

            csvData[fileKey] = csvFile.convertToObj('json')

    s3TableCreated = False

    for key in csvData.keys():
        print(f'Doing the needful for file {key}')
        status[key] = 0
        if schema == '1':
            print("Loading Schema 1")
            ddbAttributes = [{'AttributeName': 'id','AttributeType':'N'}]
            ddbKeySchema = [{'AttributeName': 'id', 'KeyType': 'HASH'}]

            if clean:
                ddb.createTable(key, ddbAttributes, ddbKeySchema, 'PAY_PER_REQUEST')
        
        elif schema == '2':
            print("Loading Schema 2")
            ddbAttributes = [{'AttributeName': 'artist_name', 'AttributeType': 'S'},{'AttributeName': 'id', 'AttributeType': 'N'},{'AttributeName': 'title', 'AttributeType': 'S'},{'AttributeName': 'year', 'AttributeType': 'N'},{'AttributeName': 'format', 'AttributeType': 'S'},{'AttributeName': 'price', 'AttributeType': 'N'}]
            ddbKeySchema = [{'AttributeName': 'artist_name', 'KeyType': 'HASH'}, {'AttributeName': 'id', 'KeyType': 'RANGE'}]
            ddbLSI = [
                {
                    'IndexName': 'artist_name-title-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'artist_name',
                            'KeyType': 'HASH'
                        },{
                            'AttributeName': 'title',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }, 
                {
                    'IndexName': 'artist_name-year-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'artist_name',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'year',
                            'KeyType': 'RANGE'
                        }
                    ], 
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
            ddbGSI = [
                {
                    'IndexName': 'format-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'format',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'price-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'price',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'title-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'title',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'year-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'year',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
            
            if clean:
                ddb.createTable(key, ddbAttributes, ddbKeySchema, 'PAY_PER_REQUEST', clean, GSI = ddbGSI, LSI = ddbLSI)
        
        elif schema == '3':
            if not s3TableCreated:
                print("Loading Schema 3")
                ddbAttributes = [{'AttributeName': 'type', 'AttributeType': 'S'},{'AttributeName': 'id', 'AttributeType': 'N'},{'AttributeName': 'name_title', 'AttributeType': 'S'},{'AttributeName': 'year', 'AttributeType': 'N'},{'AttributeName': 'format', 'AttributeType': 'S'},{'AttributeName': 'price', 'AttributeType': 'N'}]
                ddbKeySchema = [{'AttributeName': 'type', 'KeyType': 'HASH'}, {'AttributeName': 'id', 'KeyType': 'RANGE'}]
                ddbLSI = [
                    {
                        'IndexName': 'type-name_title-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'type',
                                'KeyType': 'HASH'
                            },{
                                'AttributeName': 'name_title',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ]
                ddbGSI = [
                    {
                        'IndexName': 'format-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'format',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    },
                    {
                        'IndexName': 'price-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'price',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    },
                    {
                        'IndexName': 'name_title-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'name_title',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    },
                    {
                        'IndexName': 'year-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'year',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ]

                if clean:
                    ddb.createTable('pinehead_records_s3', ddbAttributes, ddbKeySchema, 'PAY_PER_REQUEST', clean, GSI = ddbGSI, LSI = ddbLSI)
                    s3TableCreated = True
            else:
                print("Needful already done for pinehead_records_s3 table creation! ONWARD!!! \\m/")

        itemCount = len(csvData[key])
        chunkSize = itemCount // workerProcesses
        extraChunk = itemCount % workerProcesses
        if extraChunk != 0:
            extraChunk = int(extraChunk) + 1
        
        iters = itemCount // chunkSize

        for i in range(iters):
            chunkStart = chunkSize * i
            chunkEnd = chunkSize * (i + 1)
            chunk = csvData[key][chunkStart:chunkEnd]
            
            if schema == '3':
                tablename = 'pinehead_records_s3'
                schema3 = key
            else:   
                tablename = key
                schema3 = None

            tableArgs.append((tablename, 0, 0, status, chunk, schema3))
            
    random.shuffle(tableArgs)
    print('[!]: Starting Migration')
    startTime = int(time())
    processPool.starmap(worker, tableArgs)
    finishTime = int(time())
    totalSeconds = finishTime - startTime
    totalMinutes = totalSeconds // 60
    totalSeconds = totalSeconds % 60
    print(f'[!]: Migration took {totalMinutes} minutes {totalSeconds} seconds')

if __name__ == '__main__':
    main()