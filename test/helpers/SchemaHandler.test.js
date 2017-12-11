/* eslint-disable semi */
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { schemaHandler, fetchSchema } from '../../src/helpers/SchemaHandler'
import TransformerError from '../../src/helpers/ErrorHelper'
import chai from 'chai'
import chaiAsPromised from 'chai-as-promised'
chai.should()
chai.use(chaiAsPromised)

describe('AvroToJsonTransformer Lambda: SchemaHandler', () => {
  let mock

  beforeEach(() => {
    mock = new MockAdapter(axios)
  })

  afterEach(() => {
    mock.reset()
  })

  describe('schemaHandler(cachedSchema, fetchSchemaFn)', () => {
    it('should not fetch a new schema if cachedSchema contains one', () => {
      let result = schemaHandler('cachedSchemaJson', 'fetchSchemaFn')
      return result.should.be.fulfilled.and.should.eventually.deep.equal({
        schemaType: 'cached-schema',
        schema: 'cachedSchemaJson'
      })
    })

    it('should fetch a new schema when cachedSchema is null', () => {
      mock.onGet().reply(
        200,
        {
          data: {
            schema: '{ "name": "circTrans" }'
          }
        }
      )

      let result = schemaHandler(null, fetchSchema('http://nypltest.org', 'schema-path', 'schema'))

      return result.should.be.fulfilled.and.should.eventually.deep.equal({
        schemaType: 'fresh-schema',
        schema: JSON.parse('{ "name": "circTrans" }')
      })
    })

    it('should reject the promise on 400 responses from the API', () => {
      mock.onGet().reply(404)

      let result = schemaHandler(null, fetchSchema('http://nypltest.org', 'schema-path', 'schema'))

      return result.should.be.rejected.and.should.eventually.have.property('statusCode', 404)
    })

    it('should reject the promise on 500 responses from the API', () => {
      mock.onGet().reply(503)

      let result = schemaHandler(null, fetchSchema('http://nypltest.org', 'schema-path', 'schema'))

      return result.should.be.rejected.and.should.eventually.have.property('statusCode', 503)
    })
  })

  describe('fetchSchema(url, path, name)', () => {
    it('should reject the promise if the url parameter is undefined', () => {
      let result = fetchSchema(null, 'path', 'name')
      return result.should.be.rejectedWith(TransformerError, 'missing one or more URL parameters')
    })

    it('should reject the promise if the path parameter is undefined', () => {
      let result = fetchSchema('url', null, 'name')
      return result.should.be.rejectedWith(TransformerError, 'missing one or more URL parameters')
    })

    it('should reject the promise if the name parameter is undefined', () => {
      let result = fetchSchema('url', 'path', null)
      return result.should.be.rejectedWith(TransformerError, 'missing one or more URL parameters')
    })

    it('should reject the promise if the response is empty', () => {
      mock.onGet().reply(
        200,
        {}
      )

      let result = fetchSchema('http://nypltest.org', 'schema-path', 'schema')
      return result.should.be.rejectedWith(TransformerError, 'Schema object could not be retrieved')
    })

    it('should reject the promise if the schema object is undefined', () => {
      mock.onGet().reply(
        200,
        {
          data: {}
        }
      )

      let result = fetchSchema('http://nypltest.org', 'schema-path', 'schema')
      return result.should.be.rejectedWith(TransformerError, 'Schema object could not be retrieved')
    })
  })
})
