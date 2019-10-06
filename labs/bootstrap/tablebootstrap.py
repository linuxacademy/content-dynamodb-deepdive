import argparse, random, json, csv
import boto3
import pymysql, pymysql.cursors
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

    def createTable(self, tableName, attributes, keySchema, billingMode, clean, provisionedThroughput = {}):
        print(f'[!]: Creating {tableName}')
        if clean:
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
                self.client.create_table(
                    AttributeDefinitions = attributes,
                    KeySchema = keySchema,
                    BillingMode = billingMode,
                    TableName = tableName
                )

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

def worker(source, table, chunkStart, chunkEnd, dbParams, schema, status, data = None):
    ddb = DynamoDB()
    procName = current_process().name
    typeConversion = {
            'int': 'N',
            'decimal.Decimal': 'N',
            'Decimal': 'N',
            'float': 'N',
            'str': 'S',
            'bytes': 'B'
        }

    if source == 'csv':
        data = data
    
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
           
            for k,v in row.items():
                batchDataSize += getsizeof(v)

                if type(v).__name__ == 'NoneType' or v == '':
                    continue
                
                try:
                    putItem['PutRequest']['Item'][k] = {
                        typeConversion[type(v).__name__]: str(v)
                    }
                except Exception as e:
                    print(f'[-]: {procName} Error generating putItem object - {e}')
                    print(row)

            if table == 'album':
                album_id = str(row['id'])
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

        status[table] += 25

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--processes', type = int, default = 32, help = "Number of processes to use")
    ap.add_argument('-s', '--schema', required = True, choices = ['1', '2'], help = 'Schema to migrate to (1 or 2)')
    ap.add_argument('-o', '--origin', required = True, choices = ['csv', 'mysql'], help = 'Specify source (csv, or mysql)')
    ap.add_argument('-c', '--clean', choices = ['True', 'False'], default = 'True', help = 'Specify if existing tables should be deleted')
    ap.add_argument('-f', '--file', help = 'Location of csv file(s) if source is csv')
    args = vars(ap.parse_args())

    workerProcesses = args['processes']
    processPool = Pool(processes = workerProcesses)
    source = args['origin']
    schema = args['schema']
    clean = bool(args['clean'])
    tableArgs = []

    if args['origin'] == 'csv':
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

        for key in csvData.keys():
            status[key] = 0
            ddbAttributes = [{'AttributeName': 'id','AttributeType':'N'}]
            ddbKeySchema = [{'AttributeName': 'id', 'KeyType': 'HASH'}]
                
            ddb.createTable(key, ddbAttributes, ddbKeySchema, 'PAY_PER_REQUEST', clean)
            
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
                tableArgs.append(('csv', key, 0, 0, 'none', 1, status, chunk))
            
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