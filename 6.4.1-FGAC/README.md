# 6.4.1 - Fine Grained Access Control (FGAC)

- `access-specific-attributes.json` - This permissions policy allows access to only specific attributes in a table by adding the `dynamodb:Attributes` condition key. These attributes can be read or evaluated in a conditional scan filter.

- `access-specific-table.json` - This permissions policy grants permissions that allow a set of DynamoDB actions on the `pinehead_records_s3` table.
