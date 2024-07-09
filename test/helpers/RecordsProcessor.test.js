const fs = require('fs')

const { processRecords } = require('../../src/helpers/RecordsProcessor.js')

const schema = JSON.parse(fs.readFileSync('./test/stubs/CircTrans.json', 'utf8'))
const records = JSON.parse(fs.readFileSync('./test/stubs/records.json', 'utf8'))

describe('Records Processor: processRecords(schema, records)', () => {
  it('should return JSON array of 3 sample objects; 2 successes and 1 failure', () => {
    const result = processRecords(schema, records.records)
    console.log('result:', result)

    let jsn = false
    const buf = Buffer.from(result[0].data, 'base64')
    if (JSON.parse(buf)) {
      jsn = true
    }

    expect(Array.isArray(result)).to.equal(true)
    expect(jsn).to.equal(true)
    expect(result.length).to.equal(3)
    expect(result[0].recordId).to.be.equal('789')
    expect(result[0].result).to.equal('Ok')
    expect(result[0].data).to.be.a('string')
    expect(result[2].result).to.equal('ProcessingFailed')
  })
})
