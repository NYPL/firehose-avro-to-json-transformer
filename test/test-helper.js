const chai = require('chai')
const chaiAsPromised = require('chai-as-promised')
const sinonChai = require('sinon-chai')

chai.should()
chai.use(sinonChai)
chai.use(chaiAsPromised)

global.expect = chai.expect

let envCache = {}

/**
 * Stores the given values in process.env
 */
function setEnv (hash) {
  Object.keys(hash).forEach((k) => {
    envCache[k] = process.env[k]
    process.env[k] = hash[k]
  })
}

/**
 * After calling `setEnv`, use this to restore process.env to the former state
 */
function restoreEnv () {
  Object.keys(envCache).forEach((k) => {
    if (typeof envCache[k] === 'undefined') {
      delete process.env[k]
    } else {
      process.env[k] = envCache[k]
    }
  })
  envCache = {}
}

/**
 *  Given a base64 encoded, stringified JSON, returns the JSON object.
 */
// const decodeBase64Json = (v) => JSON.parse(Buffer.from(v, 'base64'))
const decodeBase64Json = (v) => {
  const s = Buffer.from(v, 'base64').toString('utf8')
  return JSON.parse(s)
}

module.exports = {
  setEnv,
  restoreEnv,
  decodeBase64Json
}
