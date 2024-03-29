const axios = require('axios')
const MockAdapter = require('axios-mock-adapter')

const { schemaHandler, fetchSchema } = require('../../src/helpers/SchemaHandler.js')
const TransformerError = require('../../src/helpers/ErrorHelper.js')

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
      const result = schemaHandler('cachedSchemaJson', 'fetchSchemaFn')
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

      const result = schemaHandler(null, fetchSchema('http://nypltest.org', 'schema-path', 'schema'))

      return result.should.be.fulfilled.and.should.eventually.deep.equal({
        schemaType: 'fresh-schema',
        schema: JSON.parse('{ "name": "circTrans" }')
      })
    })

    it('should reject the promise on 400 responses from the API', () => {
      mock.onGet().reply(404)

      const result = schemaHandler(null, fetchSchema('http://nypltest.org', 'schema-path', 'schema'))

      return result.should.be.rejected.and.should.eventually.have.property('statusCode', 404)
    })

    it('should reject the promise on 500 responses from the API', () => {
      mock.onGet().reply(503)

      const result = schemaHandler(null, fetchSchema('http://nypltest.org', 'schema-path', 'schema'))

      return result.should.be.rejected.and.should.eventually.have.property('statusCode', 503)
    })
  })

  describe('fetchSchema(url, path, name)', () => {
    it('should reject the promise if the url parameter is undefined', () => {
      const result = fetchSchema(null, 'path', 'name')
      return result.should.be.rejectedWith(TransformerError, 'missing one or more URL parameters')
    })

    it('should reject the promise if the path parameter is undefined', () => {
      const result = fetchSchema('url', null, 'name')
      return result.should.be.rejectedWith(TransformerError, 'missing one or more URL parameters')
    })

    it('should reject the promise if the name parameter is undefined', () => {
      const result = fetchSchema('url', 'path', null)
      return result.should.be.rejectedWith(TransformerError, 'missing one or more URL parameters')
    })

    it('should reject the promise if the response is empty', () => {
      mock.onGet().reply(
        200,
        {}
      )

      const result = fetchSchema('http://nypltest.org', 'schema-path', 'schema')
      return result.should.be.rejectedWith(TransformerError, 'Schema object could not be retrieved')
    })

    it('should reject the promise if the schema object is undefined', () => {
      mock.onGet().reply(
        200,
        {
          data: {}
        }
      )

      const result = fetchSchema('http://nypltest.org', 'schema-path', 'schema')
      return result.should.be.rejectedWith(TransformerError, 'Schema object could not be retrieved')
    })
  })
})
