const axios = require('axios')

const logger = require('./Logger.js')
const TransformerError = require('./ErrorHelper.js')

const fetchSchema = function (url, path, name) {
  if (!url || !path || !name) {
    return Promise.reject(
      new TransformerError('missing one or more URL parameters')
    )
  }

  return axios.get(url + path + name)
    .then(response => {
      if (response.data && typeof response.data.data !== 'undefined' && typeof response.data.data.schema !== 'undefined') {
        return Promise.resolve(JSON.parse(response.data.data.schema))
      }

      return Promise.reject(
        new TransformerError(
          'Schema object could not be retrieved',
          { type: 'invalid-schema-response' }
        )
      )
    })
    .catch(error => {
      let errMsg = 'An error occurred requesting the schema from the NYPL API'
      errMsg += ` (${url}${path}${name})`

      if (error.response) {
        const statusCode = error.response.status
        const statusText = error.response.statusText
        if (statusCode) {
          errMsg += `; the service responded with status code: (${statusCode})`
        }
        if (statusText) {
          errMsg += ` and status text: (${statusText})`
        }

        logger.error(errMsg, { debugInfo: error.response })
        return Promise.reject(
          new TransformerError(
            errMsg,
            {
              type: 'api-service-error',
              statusCode: error.response.status || null
            }
          )
        )
      }
      logger.error(errMsg, { debugInfo: error })
      return Promise.reject(error)
    })
}

const schemaHandler = async function (cachedSchema, getSchemaFn) {
  if (cachedSchema) {
    return {
      schemaType: 'cached-schema',
      schema: cachedSchema
    }
  }

  const freshSchema = await getSchemaFn
  return {
    schemaType: 'fresh-schema',
    schema: freshSchema
  }
}

module.exports = {
  fetchSchema,
  schemaHandler
}
