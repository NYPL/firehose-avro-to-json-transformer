import axios from 'axios'
import logger from './Logger'
import TransformerError from './ErrorHelper'

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
      let errMsg = 'An error occurred requesting from the NYPL API'

      if (error.response) {
        let statusCode = error.response.status
        let statusText = error.response.statusText
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

  try {
    const freshSchema = await getSchemaFn
    return {
      schemaType: 'fresh-schema',
      schema: freshSchema
    }
  } catch (e) {
    throw e
  }
}

export {
  fetchSchema,
  schemaHandler
}
