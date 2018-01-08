import { processRecords } from '../../src/helpers/RecordsProcessor'
import schema from '../stubs/CircTrans.json'
import records from '../stubs/records.json'
import chai from 'chai'
chai.should()
const expect = chai.expect

describe('Records Processor: processRecords(schema, records)', () => {
  it('should return JSON array of 3 sample objects; 2 successes and 1 failure', () => {
    let result = processRecords(schema, records.records)

    let jsn = false
    let buf = Buffer.from(result[0].data, 'base64')
    if (JSON.parse(buf)) {
      jsn = true
    }

    expect(Array.isArray(result)).to.equal(true)
    expect(jsn).to.equal(true)
    expect(result.length).to.equal(3)
    expect(result[0].hasOwnProperty('recordId')).to.equal(true)
    expect(result[0].hasOwnProperty('result')).to.equal(true)
    expect(result[0].hasOwnProperty('data')).to.equal(true)
    expect(result[2].result).to.equal('ProcessingFailed')
  })
})
