/* eslint-disable no-unused-expressions */

import chai from 'chai'

import Cache from '../../src/cache/CacheFactory.js'
chai.should()
const expect = chai.expect

describe('AvroToJsonTransformer Lambda: CacheFactory', () => {
  it('should initialize the nodeEnv variable', () => {
    expect(Cache.nodeEnv).to.equal(process.env.NODE_ENV)
  })

  it('should return the set value for nodeEnv variable', () => {
    const testEnv = 'local'
    Cache.setNodeEnv(testEnv)
    expect(Cache.getNodeEnv()).to.equal(testEnv)
  })

  it('should initialize schema variable as null', () => {
    expect(Cache.schemas).to.be.a('object')
    expect(Cache.schemas).to.be.empty
  })

  it('should return the set value for schema variable', () => {
    const testSchema = '{ "name": "circ_trans", "type": "record" }'
    Cache.setSchema('circ_trans', testSchema)
    expect(Cache.getSchema('circ_trans')).to.equal(testSchema)

    // Confirm it can handle another schema:
    const testSchema2 = '{ "name": "circ_trans2", "type": "record" }'
    Cache.setSchema('circ_trans2', testSchema2)
    expect(Cache.getSchema('circ_trans2')).to.equal(testSchema2)
  })
})
