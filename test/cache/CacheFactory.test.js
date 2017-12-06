/* eslint-disable semi */
import chai from 'chai'
import Cache from '../../src/cache/CacheFactory'
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
    expect(Cache.schema).to.equal(null)
  })

  it('should return the set value for schema variable', () => {
    const testSchema = '{ "name": "circ_trans", "type": "record" }'
    Cache.setSchema(testSchema)
    expect(Cache.getSchema()).to.equal(testSchema)
  })
})
