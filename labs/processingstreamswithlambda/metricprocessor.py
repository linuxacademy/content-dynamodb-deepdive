import json
import boto3

print('Loading function...')
def writestats(newrecord):
    ddbClient = boto3.client('dynamodb')
    
    try:
        currentStats = ddbClient.get_item(
            TableName = 'TaTourneyStats',
            Key = {
                'player': newrecord['player']
            }
        )
    except Exception as e:
        print(e)
        return e
    
    if 'Item' not in currentStats.keys():
        statItem = {
            'player': newrecord['player'],
            'avg_score': newrecord['score'],
            'games': {'N': '1'}
        }    
        if 'winner' in newrecord.keys():
            statItem['wins'] = {'N': '1'}
        else:
            statItem['wins'] = {'N': '0'}

        statItem['win_percent'] = {'S': f"{str((int(statItem['wins']['N']) / int(statItem['games']['N']))*100)[:5]}%"}
        print(f'New Record: {statItem}')
        try:
            ddbClient.put_item(
                TableName = 'TaTourneyStats',
                Item = statItem
            )
        except Exception as e:
            print(e)
            return e

    else:
        statItem = {
            'games': {'N': str(int(currentStats['Item']['games']['N']) + 1)}
        }

        if 'winner' in newrecord.keys():
            statItem['wins'] = {'N': '1'}
        else:
            statItem['wins'] = {'N': '0'}

        statItem['win_percent'] = {'S': f"{str(((int(currentStats['Item']['wins']['N']) + int(statItem['wins']['N'])) / int(statItem['games']['N']))*100)[:5]}%"}

        statItem['avg_score'] = {'N': str((int(currentStats['Item']['avg_score']['N']) + int(newrecord['score']['N'])) // 2)}
        print(f'Update: {statItem}')
        try:
            ddbClient.update_item(
            ExpressionAttributeValues={
                ':avs': statItem['avg_score'],
                ':win': statItem['wins'],
                ':wp': statItem['win_percent'],
                ':one': {'N': '1'}
            },
            UpdateExpression='SET avg_score = :avs, games = games + :one, wins = wins + :win, win_percent = :wp',
            Key={
                'player': newrecord['player']
            },
            TableName = 'TaTourneyStats'
        )
        except Exception as e:
            print(e)
            return e

def lambda_handler(event, context):
    for record in event['Records']:
        if 'NewImage' in record['dynamodb'].keys():
            print(json.dumps(record['dynamodb']['NewImage']))
            print(writestats(record['dynamodb']['NewImage']))

    successmsg = f'Successfully processed {len(event["Records"])} records.'
    print(successmsg)
    return successmsg