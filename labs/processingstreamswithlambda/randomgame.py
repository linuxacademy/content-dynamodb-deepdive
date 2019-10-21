from time import sleep
from datetime import datetime as date
import random
import boto3

class DynamoDB:
    def __init__(self):
        self.client = boto3.client('dynamodb')
        self.batchTrys = 0

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

def getRandomNumber(range):
    return random.randint(range[0], range[1])

def fight(player1, player2):
    p1Score = getRandomNumber((1, 1000001))
    p2Score = getRandomNumber((1, 1000001))
    return {player1: p1Score, player2: p2Score}

def main():
    ddb = DynamoDB()
    players = ['Tia', 'Julie', 'Kelby', 'Craig', 'Mike', 'Rich', 'Miles', 'John', 'Moosa', 'Mark']
    day = f'{date.now()} UTC'
    win = '1'
    game = 1

    while True:
        player1 = players[getRandomNumber((0, len(players) - 1))]
        player2 = players[getRandomNumber((0, len(players) - 1))]
        while player1 == player2:
            player2 = players[getRandomNumber((0, len(players) - 1))]

        results = fight(player1, player2)
        items = [
            {
                'game': {'N': str(game)},
                'player': {'S': player1},
                'date': {'S': day},
                'score': {'N': str(results[player1])}
            },
            {                
                'game': {'N': str(game)},
                'player': {'S': player2},
                'date': {'S': day},
                'score': {'N': str(results[player2])}
            }
        ]

        if results[player1] > results[player2]:
            items[0]['winner'] = {'N': win}
        elif results[player1] < results[player2]:
            items[1]['winner'] = {'N': win}

        for i in items:
            print(i)

        for i in range(len(items)):
            items[i] = { 'PutRequest': { 'Item': items[i] } }

        ddb.batchWrite('TaTourney', items)

        game += 1
        sleep(getRandomNumber((1,31)))


if __name__ == '__main__':
    main()