# Kinesis Firehose Avro to Json Transformer Lambda
[![Build Status](https://travis-ci.org/NYPL/firehose-avro-to-json-transformer.svg?branch=main)](https://travis-ci.org/NYPL/firehose-avro-to-json-transformer)

This app reads from Firehose Kinesis streams, decodes the records using the appropriate Avro schema based on the stream name, and returns the resulting records as either JSON or CSV (base64 encoded). This app is responsible for decoding records immediately before ingest into the [BIC](https://github.com/NYPL/BIC).

## Version
> v1.0.1

## Installation

Install all Node dependencies via NPM

```console
nvm use
npm install
```

## Running Locally

Use the [sam cli](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) to run the lambda on arbitrary firehose events. To process a firehose event containing 3 CircTrans records and print out the result:

```
sam local invoke --profile nypl-digital-dev -t sam.qa.yml -e sample/firehose-CircTrans-3-records-encoded.json
```

## Contributing

This repo uses the ["PRs Target Main, Merge to Deployment Branches" git workflow](https://github.com/NYPL/engineering-general/blob/main/standards/git-workflow.md#prs-target-main-merge-to-deployment-branches):
 - Cut PRs from `main`
 - Merge `main` > `qa`
 - Merge `main` > `production`

## Deployment

This app is deployed via Travis-CI using terraform. Code in `qa` is pushed to AvroToJsonTransformer-qa. Code in `main` is pushed to AvroToJsonTransformer-production.

## Tests

To run all tests found in `./test/`:

```console
npm run test
```

To run a specific test for the given filename:

```console
npm run test [filename].test.js
```

### Test Coverage

This repo uses c8 to compute test coverage (because [Istanbul](https://github.com/istanbuljs/nyc) doesn't appear to support ESM at writing). Coverage reports are included at the end of `npm test`. For a detailed line-by-line breakdown, view the HTML report:

```console
npm run coverage-report
open coverage/index.html
```

### Linting

This codebase uses [Standard JS](https://www.npmjs.com/package/standard) as the JavaScript linter.

To check for linting errors:

```console
npm run lint
```
