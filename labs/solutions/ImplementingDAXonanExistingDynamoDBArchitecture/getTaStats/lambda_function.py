import boto3
from botocore.config import Config
from amazondax import AmazonDaxClient
print("Starting function...")

# --- EDIT ---

endpoint = 'DAXENDPOINT'
config = Config(retries=dict(max_attempts=1), read_timeout=20)
ddbClient = AmazonDaxClient(endpoint_url=endpoint)

# --- END ---

def deserialize(items):
    data = []

    for item in list(items):
            record = {}
            for k,v in item.items():
                for _,value in v.items():
                    if k == 'player':
                        record[k] = f'<img src=\"images\\{value}.jpg\"><br>{value}'
                    else:
                        if '.' in value:
                            try:
                                record[k] = float(value)
                            except ValueError:
                                record[k] = value
                        else:
                            try:
                                record[k] = int(value)
                            except ValueError:
                                record[k] = value
            data.append(record)
    
    return data

def scanTable():
    try:
        items = ddbClient.scan(TableName='TaTourneyStats', ProjectionExpression='player,avg_score,games,wins,win_percent')['Items']
        return items
    except Exception:
        return [{ 'player': "<img src=\"images/spinner.gif\">", 'avg_score': "<img src=\"images/spinner.gif\">", 'games': "<img src=\"images/spinner.gif\">", 'wins': "<img src=\"images/spinner.gif\">", 'win_percent': "<img src=\"images/spinner.gif\">"}]

def getStats():
    items = scanTable()

    if len(items) > 1:
        data = deserialize(items)
    else:
        data = items
    
    ordered = sorted(data, key = lambda i: i['wins'], reverse=True)
    return ordered

def lambda_handler(event, context):
    stats = getStats()
    print(stats)
    return stats