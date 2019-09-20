import csv, argparse, json, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required = True, help = "Csv File to convert to JSON objects")
    ap.add_argument('-o', '--output', choices = ['json', 'dynamodb'], required = True, help = "Output in JSON, or DynamoDB-Json")
    args = vars(ap.parse_args())
    
    csvFile = open(args['file'])
    csvLines = csvFile.readlines()
    headLine = csvLines[0]

    if '*' in headLine:
        csvData = list(csv.reader(open(args['file']), delimiter = '*', quotechar = '#', escapechar = '\\'))
    if ',' in headLine:
        csvData = list(csv.reader(open(args['file'])))

    headings = csvData[0]
    pets = []

    for i in range(len(csvData)):
        dataDict = {}
        if i > 0:
            for v in range(len(csvData[i])):
                # Prints line/field indexes used for troubleshooting.
                # print(f'{i}:{v}')
                if csvData[i][v] == 'Null' or csvData[i][v] == None:
                    continue

                value = csvData[i][v]
                if '.' in value:
                    try:
                        dataDict[headings[v]] = float(value)
                    except ValueError:
                        dataDict[headings[v]] = value
                else:
                    try:
                        dataDict[headings[v]] = int(value)
                    except ValueError:
                        dataDict[headings[v]] = value
                
                if '\\"' in value:
                    re.sub('\\"', '', value)

            if args['output'] == 'dynamodb':
                for key, value in dataDict.items():
                    if isinstance(value, int) or isinstance(value, float):
                        dataDict[key] = {'N': value}
                    elif isinstance(value, str):
                        dataDict[key] = {'S': value}
                    else:
                        print('Error, invalid datatype!')
                        return
                pets.append(dataDict)
            else:    
                pets.append(dataDict)

    for i in pets:
        print(json.dumps(i, sort_keys = True, indent = 4, separators = (',', ': ')))
    
if __name__ == '__main__':
    main()