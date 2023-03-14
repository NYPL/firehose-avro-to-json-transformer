const avro = require('avsc')

const logger = require('./Logger.js')

// Map records to decode Avro and return data in desired output format to firehose.
const processRecords = function (schema, records, outputFormat) {
  let success = 0
  let failure = 0
  const type = avro.Type.forSchema(schema)
  const output = records.map((record) => {
    const decodedData = decodeAvro(type, record.data)
    if (!decodedData) {
      failure++
      return {
        recordId: record.recordId,
        result: 'ProcessingFailed',
        data: record.data
      }
    }

    let resultString = ''
    if (outputFormat === 'csv') {
      Object.values(decodedData).forEach((value) => {
        if (value === null) {
          value = ''
        } else if (typeof value === 'string') {
          value = value.replace('|', '\\|')
        }
        resultString += (value + '|')
      })
      resultString = resultString.slice(0, -1)
    } else {
      resultString = JSON.stringify(decodedData)
    }

    success++
    return {
      recordId: record.recordId,
      result: 'Ok',
      data: Buffer.from(resultString).toString('base64')
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

module.exports = {
  processRecords,
  decodeAvro
}
