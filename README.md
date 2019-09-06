# Amazon DynamoDB Deep Dive Course

## Pinehead Records Sample Web App Evolution

### [webapp-v0](./webapp-v0) - Relational/Legacy

- Relational model in MySQL
- limited optimizations
- limited caching
- no indexes
- inefficient queries
- images stored on local filesystem
- accounts in DB

### [webapp-v1](./webapp-v1) - Fundamental DynamoDB

- Naïve migration from MySQL to DynamoDB
- 3 DDB tables mimicking the relational structure
- images are moved to S3 with URI in DDB attribute
- no indexes
- accounts in DB

### [webapp-v2](./webapp-v2) - Intermediate DynamoDB

- some optimizations
- better table structure (single hierarchical table)
- indexes
- transactions
- accounts in DB

### [webapp-v3](./webapp-v3) - Advanced DynamoDB

- federated web identity (Cognito)
- fine-grained policies
- triggers
- improved security
- DAX

