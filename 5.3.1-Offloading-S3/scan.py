#!/usr/bin/env python3

from time import time

import boto3


def scan(tableName):
    ddbClient = boto3.client("dynamodb")

    startTime = time()
    totalCapacity = 0
    totalCount = 0

    try:
        queryResponse = ddbClient.scan(
            TableName=tableName, ReturnConsumedCapacity="TOTAL"
        )
    except Exception as e:
        return e

    totalCapacity += queryResponse["ConsumedCapacity"]["CapacityUnits"]
    totalCount += queryResponse["Count"]

    for _ in range(9):
        try:
            queryResponse = ddbClient.scan(
                TableName=tableName, ReturnConsumedCapacity="TOTAL"
            )
        except Exception as e:
            return e

        totalCapacity += queryResponse["ConsumedCapacity"]["CapacityUnits"]
        totalCount += queryResponse["Count"]

    queryResponse["ConsumedCapacity"]["CapacityUnits"] = totalCapacity
    queryResponse['Count'] = totalCount

    endTime = time()
    opTime = {"seconds": 0}
    opTime["seconds"] = endTime - startTime
    if opTime["seconds"] > 60:
        opTime["minutes"] = opTime["seconds"] // 60
        opTime["seconds"] = opTime["seconds"] % 60

    if "minutes" in opTime.keys():
        return f'Query/Scan complete in {opTime["minutes"]} Minutes {opTime["seconds"]} Seconds\nyRead Capacity Consumed: {queryResponse["ConsumedCapacity"]["CapacityUnits"]} Capacity Units\nItems Returned: {queryResponse["Count"]}'
    else:
        return f'Query/Scan complete in {int(opTime["seconds"] * 1000)} Milliseconds\nRead Capacity Consumed: {queryResponse["ConsumedCapacity"]["CapacityUnits"]} Capacity Units\nItems Returned: {queryResponse["Count"]}'


def main():
    print("\nTesting Scan time and read capacity unit usage:")
    for table in ["album", "album_bin"]:
        print(f'Scanning: {table}')
        print(scan(table))


if __name__ == "__main__":
    main()
