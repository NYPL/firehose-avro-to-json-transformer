/* eslint-disable semi */
const cache = {
  schema: null,
  nodeEnv: process.env.NODE_ENV,
  getSchema () {
    return this.schema
  },
  setSchema (schema) {
    this.schema = schema
  },
  getNodeEnv () {
    return this.nodeEnv
  },
  setNodeEnv (env) {
    this.nodeEnv = env
  }
}

export default cache
