import argparse, random, json, csv
import boto3
import pymysql, pymysql.cursors
from time import time, sleep
from sys import getsizeof
from multiprocessing import Pool, Manager, current_process, active_children

class MySQL:
    def __init__(self, dbParams):
        self.dbParams = dbParams
        self.con = pymysql.connect(
            host=dbParams['host'],
            user=dbParams['username'],
            password=dbParams['password'],
            db=dbParams['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.con.cursor()
        self.tables = {}
    
    def __del__(self):
        self.cursor.close()
        self.con.close()

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def scanSchema(self):
        showTables = self.query('SHOW TABLES')
        for row in showTables:
            database = self.dbParams['database']
            self.tables[row[f'Tables_in_{database}']] = {}
        
        for table in self.tables.keys():
            self.tables[table]['columns'] = []
            
            describeTable = self.query(f'DESCRIBE {table}')
            for row in describeTable:
                self.tables[table]['columns'].append(row['Field'])
                if row['Key'] == 'PRI':
                    self.tables[table]['primarykey'] = row['Field']
            
            rowCount = self.query(f'SELECT COUNT(0) FROM {table}')
            for row in rowCount:
                self.tables[table]['rows'] = row['COUNT(0)']

    def getSchemaInfo(self):
        if len(self.tables) == 0:
            self.scanSchema()
        return self.tables
        
    def getDataChunkS1(self, table, start, end):
        if start > 0:
            start -= 1

        if end < start:
            return f'Error: end is before beginning {start} > {end}'

        chunkSize = end - start
        if table == 'album':
            dataChunk = self.query(f'SELECT id, sku, artist_id, title, year, format, price FROM {table} LIMIT {start}, {chunkSize}')
        else:
            dataChunk = self.query(f'SELECT * FROM {table} LIMIT {start}, {chunkSize}')

        return dataChunk

    def getDataChunkS2(self, start, end):
        if end < start:
            return f'Error: end is before beginning {start} > {end}'

        chunkSize = end - start
        return self.query(f'SELECT artist.name AS \'ArtistName\', album.id as \'AlbumID\', album.title AS \'AlbumTitle\', album.year AS \'AlbumYear\', album.format AS \'AlbumFormat\', album.price AS \'AlbumPrice\', GROUP_CONCAT(track.name) AS \'TrackNames\', CONCAT(\'TrackNames:\',GROUP_CONCAT(track.name),\', TrackLengths:\',GROUP_CONCAT(track.length),\', TrackNumbers:\',GROUP_CONCAT(track.number)) AS \'TrackInformation\' FROM artist JOIN album ON album.artist_id=artist.id JOIN track ON track.album_id=album.id GROUP BY album.id LIIMIT {start}, {chunkSize}')

class csvUtil:
    def __init__(self, inputData):
        self.csvData = list(csv.reader(inputData, delimiter = '*', quotechar = '#', escapechar = '\\'))
    
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

    if source == 'mysql':
        mysql = MySQL(dbParams)
        if schema == '1':
            data = mysql.getDataChunkS1(table, chunkStart, chunkEnd)
        if schema == '2':
            data = mysql.getDataChunkS2(chunkStart, chunkEnd)
    elif source == 'csv':
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
    ap.add_argument('-d', '--host', help = 'Hostname for MySQL server for mysql origin')
    ap.add_argument('-u', '--user', help = 'Username for MySQL server for mysql origin')
    ap.add_argument('-P', '--password', help = 'Password for MySQL server for mysql origin')
    ap.add_argument('-n', '--database', help = 'Source database to migrate')
    ap.add_argument('-f', '--file', help = 'Location of csv file(s) if source is csv')
    args = vars(ap.parse_args())

    workerProcesses = args['processes']
    processPool = Pool(processes = workerProcesses)
    source = args['origin']
    schema = args['schema']
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
                
            ddb.createTable(key, ddbAttributes, ddbKeySchema, 'PAY_PER_REQUEST', True)
            
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

    if args['origin'] == 'mysql':
        ifArg = 'if origin argument is mysql'
        if args['host'] == None:
            print(f'{ifArg} -d/--host must be provided')
            return
        if args['user'] == None:
            print(f'{ifArg} -u/--user must be provided')
            return
        if args['password'] == None:
            print(f'{ifArg} -P/--password must be provided')
            return
        if args['database'] == None:
            print(f'{ifArg} -n/--database must be provided')
            return
    
        dbParams = {
            'host': args['host'],
            'username': args['user'],
            'password': args['password'],
            'database': args['database']
        }
        
        mysql = MySQL(dbParams)
        ddb = DynamoDB()
        schemaInfo = mysql.getSchemaInfo()
        
        status = Manager().dict()

        if schema == '1':
            totalRows = 0

            for table in schemaInfo.items():
                totalRows += table[1]['rows']

            chunkSize = (totalRows // workerProcesses) // len(schemaInfo.keys())

            for table in schemaInfo.keys():
                status[table] = 0
                ddbAttributes = [{'AttributeName': schemaInfo[table]['primarykey'],'AttributeType':'N'}]
                ddbKeySchema = [{'AttributeName': schemaInfo[table]['primarykey'], 'KeyType': 'HASH'}]
                
                ddb.createTable(table, ddbAttributes, ddbKeySchema, 'PAY_PER_REQUEST', True)
                
                tableRows = schemaInfo[table]['rows']
                extraChunk = tableRows % chunkSize
                print(f'[!]: Chunk Size - {chunkSize}\n     Extra Chunk - {extraChunk}')
                if extraChunk != 0:
                    if extraChunk - int(extraChunk) != 0:
                        extraChunk = int(extraChunk) + 1
                    
                iters = tableRows // chunkSize
                
                chunkStart = 0
                chunkEnd = chunkSize
                for _ in range(iters):
                    tableArgs.append((source, table, chunkStart, chunkEnd, dbParams, schema, status))
                    chunkStart += chunkSize
                    chunkEnd += chunkSize
                if extraChunk > 0:
                    chunkStart += chunkSize
                    chunkEnd += extraChunk
                    tableArgs.append((source, table, chunkStart, chunkEnd, dbParams, schema, status))
            
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