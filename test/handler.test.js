/* eslint-env mocha */
/* eslint-disable no-unused-expressions */

const fs = require('fs')
const axios = require('axios')
const sinon = require('sinon')
const MockAdapter = require('axios-mock-adapter')

const AvroToJsonTransformer = require('../index.js')
const { setEnv, restoreEnv, decodeBase64Json } = require('./test-helper.js')

const circTransEvent = JSON.parse(fs.readFileSync('./sample/firehose-CircTrans-3-records-encoded.json', 'utf8'))
const pcReserveEvent = JSON.parse(fs.readFileSync('./sample/firehose-PcReserve-3-records-encoded.json', 'utf8'))

const recordsHandlerFn = AvroToJsonTransformer.recordsHandler
const configHandlerFn = AvroToJsonTransformer.configHandler

describe('AvroToJsonTransformer Lambda: Handle Firehose Input', () => {
  describe('Main Handler: exports.handler()', () => {
    let mock
    beforeEach(() => {
      mock = new MockAdapter(axios)

      setEnv({
        NYPL_DATA_API_BASE_URL: 'https://example.com',
        SCHEMA_PATH: '/schemas/'
      })
    })

    afterEach(() => {
      mock.reset()

      restoreEnv()
    })

    it('should return an error callback when event.records is null or missing', () => {
      const callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler(null, null, callbackSpy)

      const errArg = callbackSpy.firstCall.args[0]

      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('event is undefined')
      expect(callbackSpy).to.be.called
    })

    it('should throw an error if the event.records array is empty', () => {
      const callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler({
        sourceKinesisStreamArn: 'arn:...:stream/NonsenseStream-production',
        records: []
      },
      null,
      callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('event is undefined')
      expect(callbackSpy).to.be.called
    })

    it('should throw an error if the event.records.data array is empty', () => {
      const callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler({
        sourceKinesisStreamArn: 'arn:...:stream/NonsenseStream-production',
        records: [
          {
            data: ''
          }
        ]
      },
      null,
      callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('event.records array is empty')
      expect(callbackSpy).to.be.called
    })

    it('should callback with decoded CircTrans records', () => {
      mock.onGet().reply(
        200,
        JSON.parse(fs.readFileSync('./test/stubs/CircTrans-schema-response.json', 'utf8'))
      )

      const callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler(
        circTransEvent,
        null,
        callbackSpy
      )

      // A success callback invocation is technically async, so let things resolve:
      setImmediate(() => {
        expect(callbackSpy).to.be.called

        const errArg = callbackSpy.firstCall.args[0]
        expect(errArg).to.be.null

        const payload = callbackSpy.firstCall.args[1]
        expect(payload).to.be.a('object')
        expect(payload.records).to.be.a('array')
        expect(payload.records).to.have.lengthOf(3)
        payload.records.forEach((record) => {
          expect(record.data).to.be.a('string')
          expect(decodeBase64Json(record.data)).to.be.a('object')
          expect(decodeBase64Json(record.data).uuid).to.be.a('string')
        })
      })
    })

    it('should callback with decoded PcReserve records', () => {
      mock.onGet().reply(
        200,
        JSON.parse(fs.readFileSync('./test/stubs/PcReserve-schema-response.json', 'utf8'))
      )

      const callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler(
        pcReserveEvent,
        null,
        callbackSpy
      )

      // A success callback invocation is technically async, so let things resolve:
      setImmediate(() => {
        expect(callbackSpy).to.be.called

        const errArg = callbackSpy.firstCall.args[0]
        expect(errArg).to.be.null

        const payload = callbackSpy.firstCall.args[1]
        expect(payload).to.be.a('object')
        expect(payload.records).to.be.a('array')
        expect(payload.records).to.have.lengthOf(3)
        payload.records.forEach((record) => {
          expect(record.data).to.be.a('string')
          expect(decodeBase64Json(record.data)).to.be.a('object')
          expect(decodeBase64Json(record.data).key).to.be.a('string')
        })
      })
    })

    it('should callback with error if invalid schema name is identified', () => {
      mock.onGet().reply(404, '')

      const callbackSpy = sinon.spy()

      const eventWithNonExistentSchema = Object.assign(
        {},
        pcReserveEvent,
        { sourceKinesisStreamArn: 'arn:...:stream/NonExistentSchemaName-production' }
      )

      AvroToJsonTransformer.handler(
        eventWithNonExistentSchema,
        null,
        callbackSpy
      )

      // A success callback invocation is technically async, so let things resolve:
      setImmediate(() => {
        expect(callbackSpy).to.be.called

        const errArg = callbackSpy.firstCall.args[0]
        expect(errArg).to.be.instanceOf(Error)
        expect(errArg.message).to.equal('An error occurred requesting the schema from the NYPL API (https://example.com/schemas/NonExistentSchemaName); the service responded with status code: (404)')
        expect(callbackSpy).to.be.called

        expect(callbackSpy.firstCall.args[1]).to.be.null
      })
    })
  })

  describe('Config Handler: exports.configHandler()', () => {
    it('should respond with a TransformerError if parameter options are null', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(circTransEvent.records, null, null, callbackSpy)

      const errArg = callbackSpy.firstCall.args[0]

      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined opts object configuration parameter')
    })

    it('should respond with a TransformerError if parameter options are empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(circTransEvent.records, {}, null, callbackSpy)

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined opts object configuration parameter')
    })

    it('should respond with a TransformerError if nyplDataApiBaseUrl is missing', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          schemaPath: 'path/to/schema',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined nyplDataApiBaseUrl config parameter')
    })

    it('should respond with a TransformerError if nyplDataApiBaseUrl is not a string', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 192871,
          schemaPath: 'path/to/schema',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined nyplDataApiBaseUrl config parameter')
    })

    it('should respond with a TransformerError if nyplDataApiBaseUrl is empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: '',
          schemaPath: 'path/to/schema',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined nyplDataApiBaseUrl config parameter')
    })

    it('should respond with a TransformerError if schemaPath is missing', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined schemaPath config parameter')
    })

    it('should respond with a TransformerError if schemaPath is not a string', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaPath: 99817,
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined schemaPath config parameter')
    })

    it('should respond with a TransformerError if schemaPath is empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaPath: '',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined schemaPath config parameter')
    })

    it('should respond with a TransformerError if schemaName is missing', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaPath: 'path/to/schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined schemaName config parameter')
    })

    it('should respond with a TransformerError if schemaName is not a string', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaPath: 'path/to/schema',
          schemaName: 52223
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined schemaName config parameter')
    })

    it('should respond with a TransformerError if schemaName is empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaPath: 'path/to-schema',
          schemaName: ''
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('missing/undefined schemaName config parameter')
    })
  })

  describe('Records Handler: exports.recordsHandler(records, opts, context, callback)', () => {
    let mock
    beforeEach(() => {
      mock = new MockAdapter(axios)
    })

    afterEach(() => {
      mock.reset()
    })

    it('should be a function', () => {
      expect(recordsHandlerFn).to.be.a('function')
    })

    it('should reject an improper response from schema retrieval promise', async () => {
      await expect(recordsHandlerFn(
        circTransEvent.records,
        {
          nyplDataApiBaseUrl: 'https://nyplurl.org',
          schemaPath: 'current-schemas/',
          schemaName: 'circTrans'
        },
        null,
        null
      )).to.be.rejected
    })

    it('should handle a CircTrans batch', async () => {
      mock.onGet().reply(
        200,
        JSON.parse(fs.readFileSync('./test/stubs/CircTrans-schema-response.json', 'utf8'))
      )

      const result = await new Promise((resolve, reject) => {
        recordsHandlerFn(
          circTransEvent.records,
          {
            nyplDataApiBaseUrl: 'https://nyplurl.org',
            schemaPath: 'current-schemas/',
            schemaName: 'CircTrans'
          },
          null,
          (e, result) => {
            if (e) return reject(e)
            return resolve(result)
          })
      })

      expect(result).to.be.a('object')
      expect(result.records).to.be.a('array')
      expect(result.records).to.have.lengthOf(3)
      result.records.forEach((record) => {
        expect(record).to.be.a('object')
        expect(record.data).to.be.a('string')
        expect(decodeBase64Json(record.data)).to.be.a('object')
        expect(decodeBase64Json(record.data).op_code).to.be.a('string')
      })
    })

    it('should handle a PcReserve batch', async () => {
      mock.onGet().reply(
        200,
        JSON.parse(fs.readFileSync('./test/stubs/PcReserve-schema-response.json', 'utf8'))
      )

      const result = await new Promise((resolve, reject) => {
        recordsHandlerFn(
          pcReserveEvent.records,
          {
            nyplDataApiBaseUrl: 'https://nyplurl.org',
            schemaPath: 'current-schemas/',
            schemaName: 'PcReserve'
          },
          null,
          (e, result) => {
            if (e) return reject(e)
            return resolve(result)
          })
      })

      expect(result).to.be.a('object')
      expect(result.records).to.be.a('array')
      expect(result.records).to.have.lengthOf(3)
      result.records.forEach((record) => {
        expect(record).to.be.a('object')
        expect(record.data).to.be.a('string')
        expect(decodeBase64Json(record.data)).to.be.a('object')
        expect(decodeBase64Json(record.data).patron_id).to.be.a('string')
      })
    })
  })

  describe('schemaNameFromEvent', () => {
    it('should return CircTrans for CircTransAnon-production stream', () => {
      const schemaName = AvroToJsonTransformer.schemaNameFromEvent({
        sourceKinesisStreamArn: 'arn:aws:kinesis:stream/CircTransAnon-production'
      })
      expect(schemaName).to.equal('CircTrans')
    })

    it('should return PcReserve for PcReserve-production stream', () => {
      const schemaName = AvroToJsonTransformer.schemaNameFromEvent({
        sourceKinesisStreamArn: 'arn:aws:kinesis:stream/PcReserve-production'
      })
      expect(schemaName).to.equal('PcReserve')
    })
  })
})
