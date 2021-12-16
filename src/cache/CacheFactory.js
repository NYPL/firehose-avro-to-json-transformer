const cache = {
  schemas: {},
  nodeEnv: process.env.NODE_ENV,
  getSchema (name) {
    return this.schemas[name]
  },
  setSchema (name, schema) {
    this.schemas[name] = schema
  },
  getNodeEnv () {
    return this.nodeEnv
  },
  setNodeEnv (env) {
    this.nodeEnv = env
  }
}

module.exports = cache
