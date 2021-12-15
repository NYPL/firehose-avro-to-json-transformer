import avro from 'avsc'

import logger from './Logger.js'

// Map records to decode Avro and return JSON as data to firehose.
const processRecords = function (schema, records) {
  let success = 0
  let failure = 0
  const type = avro.Type.forSchema(schema)
  const output = records.map((record) => {
    const jsonData = decodeAvro(type, record.data)
    if (!jsonData) {
      failure++
      return {
        recordId: record.recordId,
        result: 'ProcessingFailed',
        data: record.data
      }
    }
    success++
    return {
      recordId: record.recordId,
      result: 'Ok',
      data: Buffer.from(JSON.stringify(jsonData)).toString('base64')
    }
  })
  logger.info(`Processing completed.  Successful transformations -  ${success}.  Failed transformations - ${failure}.`)
  return output
}

const decodeAvro = function (type, record) {
  const decodedRecord = Buffer.from(record, 'base64')
  try {
    return type.fromBuffer(decodedRecord)
  } catch (e) {
    logger.error(`Decoding fatal error occurred: ${e.message}`, { debugInfo: e })
    return false
  }
}

export {
  processRecords,
  decodeAvro
}
