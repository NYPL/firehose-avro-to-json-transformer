const cache = require('./src/cache/CacheFactory.js')
const logger = require('./src/helpers/Logger.js')
const TransformerError = require('./src/helpers/ErrorHelper.js')
const { schemaHandler, fetchSchema } = require('./src/helpers/SchemaHandler.js')
const { processRecords } = require('./src/helpers/RecordsProcessor.js')

const recordsHandler = async function (records, opts, context, callback) {
  try {
    const schemaResponse = await schemaHandler(cache.getSchema(opts.schemaName), fetchSchema(opts.nyplDataApiBaseUrl, opts.schemaPath, opts.schemaName))

    if (schemaResponse.schemaType === 'fresh-schema') {
      cache.setSchema(opts.schemaName, schemaResponse.schema)
    }

    if (cache.getSchema(opts.schemaName)) {
      const output = processRecords(cache.getSchema(opts.schemaName), records)
      return callback(null, { records: output })
    }
  } catch (e) {
    logger.error('Schema not properly cached')
    return callback(e, null)
  }
}

const configHandler = (records, opts, context, callback) => {
  try {
    if (!opts || Object.keys(opts).length === 0) {
      throw new TransformerError(
        'missing/undefined opts object configuration parameter',
        { type: 'function-parameter-error' }
      )
    }
    if (!opts.nyplDataApiBaseUrl || typeof opts.nyplDataApiBaseUrl !== 'string' || opts.nyplDataApiBaseUrl === '') {
      throw new TransformerError(
        'missing/undefined nyplDataApiBaseUrl config parameter',
        { type: 'function-parameter-error' }
      )
    }
    if (!opts.schemaPath || typeof opts.schemaPath !== 'string' || opts.schemaPath === '') {
      throw new TransformerError(
        'missing/undefined schemaPath config parameter',
        { type: 'function-parameter-error' }
      )
    }
    if (!opts.schemaName || typeof opts.schemaName !== 'string' || opts.schemaName === '') {
      throw new TransformerError(
        'missing/undefined schemaName config parameter',
        { type: 'function-parameter-error' }
      )
    }

    return recordsHandler(records, opts, context, callback)
  } catch (e) {
    logger.error(`transformer-configuration-error: ${e.message}`)
    return callback(e, null)
  }
}

/**
 *  Given a firehose event, returns the schema name records are encoded using
 *  based on stream ARN
 *
 *  For example, given an event with:
 *    "deliverySteamArn": "arn:aws:kinesis:PcReserve-production"
 *  .. Returns:
 *    "PcReserve"
 */
const schemaNameFromEvent = (event) => {
  // Incoming sourceKinesisStreamArn look like:
  //   "arn:aws:kinesis:us-east-1:946183545209:stream/PcReserve-production"
  return event.sourceKinesisStreamArn.split(':')
    .pop()
    .replace(/^stream\//, '')
    .replace(/-[a-z]+$/, '')
    // Against convention, the "CircTransAnon" stream contains "CircTrans"
    // encoded records, so ensure that schema name is chosen:
    .replace(/^CircTransAnon$/, 'CircTrans')
}

const handler = (event, context, callback) => {
  if (event && Array.isArray(event.records) && event.records.length > 0) {
    const record = event.records[0]

    const schemaName = schemaNameFromEvent(event)
    if (record.data) {
      return configHandler(
        event.records,
        {
          nyplDataApiBaseUrl: process.env.NYPL_DATA_API_BASE_URL,
          schemaPath: process.env.SCHEMA_PATH,
          schemaName
        },
        context,
        callback
      )
    }
    logger.error('event.records array is empty')
    return callback(new Error('event.records array is empty'))
  }

  logger.error('event.records is undefined')
  return callback(new Error('event is undefined'))
}

module.exports = {
  schemaNameFromEvent,
  recordsHandler,
  configHandler,
  handler
}
