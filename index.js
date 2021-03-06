import cache from './src/cache/CacheFactory'
import logger from './src/helpers/Logger'
import TransformerError from './src/helpers/ErrorHelper'
import { schemaHandler, fetchSchema } from './src/helpers/SchemaHandler'
import { processRecords } from './src/helpers/RecordsProcessor'

exports.recordsHandler = async function (records, opts, context, callback) {
  try {
    const schemaResponse = await schemaHandler(cache.getSchema(), fetchSchema(opts.nyplDataApiBaseUrl, opts.schemaPath, opts.schemaName))

    if (schemaResponse.schemaType === 'fresh-schema') {
      cache.setSchema(schemaResponse.schema)
    }

    if (cache.getSchema()) {
      let output = processRecords(cache.getSchema(), records)
      return callback(null, { records: output })
    }
  } catch (e) {
    logger.error('Schema not properly cached')
    return callback(e.message, null)
  }
}

exports.configHandler = (records, opts, context, callback) => {
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

    return exports.recordsHandler(records, opts, context, callback)
  } catch (e) {
    logger.error(`transformer-configuration-error: ${e.message}`)
    return callback(e.message, null)
  }
}

exports.handler = (event, context, callback) => {
  if (event && Array.isArray(event.records) && event.records.length > 0) {
    const record = event.records[0]

    if (record.data) {
      return exports.configHandler(
        event.records,
        {
          nyplDataApiBaseUrl: process.env.NYPL_DATA_API_BASE_URL,
          schemaPath: process.env.SCHEMA_PATH,
          schemaName: process.env.SCHEMA_NAME
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
