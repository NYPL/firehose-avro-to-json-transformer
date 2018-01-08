/* eslint-env mocha */
import chai from 'chai'
import chaiAsPromised from 'chai-as-promised'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import sinon from 'sinon'
import sinonChai from 'sinon-chai'
import event from '../sample/sample_event.json'
import AvroToJsonTransformer from '../index'
import TransformerError from '../src/helpers/ErrorHelper'
chai.should()
chai.use(sinonChai)
chai.use(chaiAsPromised)
const expect = chai.expect

const recordsHandlerFn = AvroToJsonTransformer.recordsHandler
const configHandlerFn = AvroToJsonTransformer.configHandler

describe('AvroToJsonTransformer Lambda: Handle Firehose Input', () => {
  describe('Main Handler: exports.handler()', () => {
    it('should return an error callback when event.records is null or missing', () => {
      let callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler(null, null, callbackSpy)

      const errArg = callbackSpy.firstCall.args[0]

      expect(errArg).to.be.instanceOf(Error)
      expect(errArg.message).to.equal('event is undefined')
      expect(callbackSpy).to.be.called
    })

    it('should throw an error if the event.records array is empty', () => {
      let callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler({
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
      let callbackSpy = sinon.spy()

      AvroToJsonTransformer.handler({
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
  })

  describe('Config Handler: exports.configHandler()', () => {
    it('should respond with a TransformerError if parameter options are null', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(event.records, null, null, callbackSpy)

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.equal('missing/undefined opts object configuration parameter')
    })

    it('should respond with a TransformerError if parameter options are empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(event.records, {}, null, callbackSpy)

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.equal('missing/undefined opts object configuration parameter')
    })

    it('should respond with a TransformerError if nyplDataApiBaseUrl is missing', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
        {
          schemaPath: 'path/to/schema',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.equal('missing/undefined nyplDataApiBaseUrl config parameter')
    })

    it('should respond with a TransformerError if nyplDataApiBaseUrl is not a string', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
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
      expect(errArg).to.equal('missing/undefined nyplDataApiBaseUrl config parameter')
    })

    it('should respond with a TransformerError if nyplDataApiBaseUrl is empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
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
      expect(errArg).to.equal('missing/undefined nyplDataApiBaseUrl config parameter')
    })

    it('should respond with a TransformerError if schemaPath is missing', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaName: 'schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.equal('missing/undefined schemaPath config parameter')
    })

    it('should respond with a TransformerError if schemaPath is not a string', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
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
      expect(errArg).to.equal('missing/undefined schemaPath config parameter')
    })

    it('should respond with a TransformerError if schemaPath is empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
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
      expect(errArg).to.equal('missing/undefined schemaPath config parameter')
    })

    it('should respond with a TransformerError if schemaName is missing', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
        {
          nyplDataApiBaseUrl: 'https://nypl.org/api/stuff',
          schemaPath: 'path/to/schema'
        },
        null,
        callbackSpy
      )

      const errArg = callbackSpy.firstCall.args[0]

      expect(callbackSpy.callCount).to.equal(1)
      expect(errArg).to.equal('missing/undefined schemaName config parameter')
    })

    it('should respond with a TransformerError if schemaName is not a string', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
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
      expect(errArg).to.equal('missing/undefined schemaName config parameter')
    })

    it('should respond with a TransformerError if schemaName is empty', () => {
      const callbackSpy = sinon.spy()
      configHandlerFn(
        event.records,
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
      expect(errArg).to.equal('missing/undefined schemaName config parameter')
    })
  })

  describe('Records Handler: exports.recordsHandler(records, opts, context, callback)', () => {
    it('should be a function', () => {
      expect(recordsHandlerFn).to.be.a('function')
    })

    it('should reject an improper response from schema retrieval promise', async () => {
      await expect(recordsHandlerFn(
        event.records,
        {
          nyplDataApiBaseUrl: 'https://nyplurl.org',
          schemaPath: 'current-schemas/',
          schemaName: 'circTrans'
        },
        null,
        null
      )).to.be.rejected
    })
  })
})
