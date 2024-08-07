# Kinesis Firehose Avro to Json Transformer Lambda
[![Build Status](https://travis-ci.org/NYPL/firehose-avro-to-json-transformer.svg?branch=main)](https://travis-ci.org/NYPL/firehose-avro-to-json-transformer)

This Python application is responsible for Avro-decoding events immediately before ingestion into the [BIC](https://github.com/NYPL/BIC). Originally developed for the Data Warehouse, this is deployed as an AWS Lambda (["AvroToJsonTransformer-qa"](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/AvroToJsonTransformer-qa?tab=configuration) and ["AvroToJsonTransformer-production"](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/AvroToJsonTransformer-production?tab=configuration)). In essence, the code does the following:
 - Decodes the incoming batch of records using the corresponding Avro schema, which is determined based on the name of the incoming Kinesis stream
 - Converts said records into a hash with `recordId`, `result: 'Ok'`, and `data` containing a JSON or CSV serialization of the record, which is also base64 encoded
 - Returns processed records in this format: `{ records: [ { recordId: '[record id]', result: 'Ok', data: 'eyJmb28iOiJiYXIifQ....' }, ... ] }`

## Running Locally

Use the [sam cli](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) to run the Lambda on arbitrary Firehose events. To process a Firehose event containing 3 CircTrans records and print out the result:

```
sam local invoke --profile nypl-digital-dev -t config/sam.qa.yml -e sample/firehose-CircTrans-3-records-encoded.json
```

The [sample](./sample) folder contains sample Firehose events and their expected outcomes after Lambda event handling, so you can test the efficacy of your code with various schemas.

With Python, you also have the option of using the [python-lambda-local](https://pypi.org/project/python-lambda-local/) package for local development! You will need to create a JSON file with env variables to use said package.

## Git workflow
This repo uses the [Main-QA-Production](https://github.com/NYPL/engineering-general/blob/main/standards/git-workflow.md#main-qa-production) git workflow.

[`main`](https://github.com/NYPL/python-utils/tree/main) has the latest and greatest commits, [`qa`](https://github.com/NYPL/python-utils/tree/qa) has what's in our QA environment, and [`production`](https://github.com/NYPL/python-utils/tree/production) has what's in our production environment.

### Ideal Workflow
- Cut a feature branch off of `main`
- Commit changes to your feature branch
- File a pull request against `main` and assign a reviewer (who must be an owner)
  - Include relevant updates to pyproject.toml and README
  - In order for the PR to be accepted, it must pass all unit tests, have no lint issues, and update the CHANGELOG (or contain the `Skip-Changelog` label in GitHub)
- After the PR is accepted, merge into `main`
- Merge `main` > `qa`
- Deploy app to QA on GitHub and confirm it works
- Merge `qa` > `production`
- Deploy app to production on GitHub and confirm it works

## Test Coverage
Use the Python [coverage package](https://coverage.readthedocs.io/en/7.6.0/) to measure test coverage:
```
coverage run -m pytest
```

To see what exactly which lines are missing testing:
```
coverage report -m
```

## Linting

This codebase uses [Black](https://github.com/psf/black) as the Python linter.

To format the codebase as a whole:
```
make lint
```
