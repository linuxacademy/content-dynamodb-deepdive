import csv, argparse, json

def main():
    # Initialize argument parser, and add arguments to accept filename, and output options.
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', required = True, help = "Csv File to convert to JSON objects")
    ap.add_argument('-o', '--output', choices = ['json', 'dynamodb'], required = True, help = "Output in JSON, or DynamoDB-Json")
    args = vars(ap.parse_args())
    
    # Reads raw file to test CSV Dialect
    csvFile = open(args['file'])
    csvLines = csvFile.readlines()
    headLine = csvLines[0]

    if '*' in headLine:
        csvData = list(csv.reader(open(args['file']), delimiter = '*', quotechar = '#', escapechar = '\\'))
    if ',' in headLine:
        csvData = list(csv.reader(open(args['file'])))

    # Get headings, and initialize items list to store data.
    headings = csvData[0]
    items = []

    # Iterate through csvData by index, where i is the index of the line in the file 0...
    for i in range(len(csvData)):
        # Empty dataDict variable to store each item in JSON/DynamoDB-Json format
        dataDict = {}
        if i > 0:
            # Iterate through each record in i line in the file using index value v
            for v in range(len(csvData[i])):
                # Prints line/field indexes used for troubleshooting. Uncomment to print index values
                # print(f'{i}:{v}')

                # Test for Null or None values and disregard the Key/Value if present
                if csvData[i][v] == 'Null' or csvData[i][v] == None:
                    continue
                
                # Intitalize value variable and set equeal to the record by the i and v index values
                value = csvData[i][v]

                # If a . character is present attempt to cast the value as a float, if this fails, use the index v in the headings list as the key for dataDict and set it equal to the current value of the value variable.
                if '.' in value:
                    try:
                        dataDict[headings[v]] = float(value)
                    except ValueError:
                        dataDict[headings[v]] = value
                # Otherwise attempt to cast into an int, and like above store according to the headings list v index as the key, and either int value or value.
                else:
                    try:
                        dataDict[headings[v]] = int(value)
                    except ValueError:
                        dataDict[headings[v]] = value
            # If the output is set to dynamodb modify the records to include the data type notation included in DynamoDB-JSON.
            if args['output'] == 'dynamodb':
                for key, value in dataDict.items():
                    if isinstance(value, int) or isinstance(value, float):
                        dataDict[key] = {'N': str(value)}
                    elif isinstance(value, str):
                        dataDict[key] = {'S': value}
                    else:
                        print('Error, invalid datatype!')
                        return
            #Append the dataDict dictionary to the items list.
                items.append(dataDict)
            else:    
                items.append(dataDict)
    # for the number of items in the items list, print i as processed by the json.dumps method.
    for i in items:
        print(json.dumps(i, sort_keys = True, indent = 4, separators = (',', ': ')))
    
if __name__ == '__main__':
    main()