#!/usr/bin/env python3

import csv
from time import sleep, time

import boto3


def convertCSV(fileName):
    tableData = []

    rawData = open(fileName)
    tableList = rawData.readlines()
    rawData.close()

    totalRows = len(tableList) - 1
    csvData = csv.DictReader(tableList, delimiter="Ԙ", quotechar="ԡ")

    for row in csvData:
        if None in row.keys():
            continue
        else:
            tableData.append(dict(row))

    for item in tableData:
        keysToDel = []

        for key, value in item.items():
            if value in {"Null", "NULL", None, ""}:
                keysToDel.append(key)
            elif key == "title":
                item[key] = {"S": str(value)}
            else:
                if "." in value:
                    try:
                        value = float(value)
                        item[key] = {"N": str(value)}
                    except ValueError:
                        item[key] = {"S": str(value)}
                else:
                    try:
                        value = int(value)
                        item[key] = {"N": str(value)}
                    except ValueError:
                        item[key] = {"S": str(value)}

        for key in keysToDel:
            del item[key]

    return (tableData, totalRows)


def dynamoDBWriter(tableName, data):
    ddbClient = boto3.client("dynamodb")
    itemsCount = len(data)
    unprocessableItems = []

    for i in range(len(data)):
        data[i] = {"PutRequest": {"Item": data[i]}}

    dataBatches = [
        data[i * 25 : (i + 1) * 25] for i in range((len(data) + 25 - 1) // 25)
    ]

    for batch in dataBatches:
        try:
            response = ddbClient.batch_write_item(RequestItems={tableName: batch})
        except Exception as e:
            return f"{e}\n {batch}"

        if len(response["UnprocessedItems"]) > 0:
            batchCalls = 0
            unprocessed = True
            while unprocessed:
                batchCalls += 1

                if batchCalls > 3:
                    print(
                        f'[!]: Unprocessed Items attempt - {batchCalls}\n{response["UnprocessedItems"]}'
                    )

                timeout = 2 ** batchCalls

                if timeout > 300:
                    itemsCount -= len(response["UnprocessedItems"][tableName])
                    unprocessableItems += response["UnprocessedItems"][tableName]
                    break

                sleep(timeout)
                try:
                    response = ddbClient.batch_write_item(
                        RequestItems=response["UnprocessedItems"]
                    )
                except Exception as e:
                    print(e)

                if len(response["UnprocessedItems"]) == 0:
                    unprocessed = False

    dataBatches = None
    return (itemsCount, unprocessableItems)


def main():
    startTime = int(time())
    fileName = "album_indexed.csv"

    tableName = fileName.split(".")[0]

    print("Converting CSV Values...")
    dataToLoad = convertCSV(fileName)
    print("Loading data into table...")
    loadResults = dynamoDBWriter(tableName, dataToLoad[0])

    if isinstance(loadResults, tuple):
        print(
            f"Loaded {loadResults[0]} items into {tableName} from {fileName} which contains {dataToLoad[1]} items"
        )
        if len(loadResults[1]) > 0:
            print("The following items could not be processed:")
            for item in loadResults[1]:
                print(item)
    else:
        print(f"An error has occured:\n{loadResults}")

    endTime = int(time())
    totalSeconds = endTime - startTime
    totalMinutes = totalSeconds // 60
    remainingSeconds = totalSeconds % 60

    print(f"Loading all files took {totalMinutes} Minutes {remainingSeconds} Seconds")


if __name__ == "__main__":
    main()
