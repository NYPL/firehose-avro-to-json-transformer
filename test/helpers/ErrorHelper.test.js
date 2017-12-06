/* eslint-disable semi */
import chai from 'chai'
import TransformerError from '../../src/helpers/ErrorHelper'
chai.should()
const expect = chai.expect

describe('AvroToJsonTransformer Lambda: TransformerError', () => {
  it('should throw an error when message variable is missing', () => {
    expect(() => new TransformerError()).to.throw(/an error message is required/)
    expect(() => new TransformerError(null, {})).to.throw(/an error message is required/)
    expect(() => new TransformerError({})).to.throw(/an error message is required/)
  })

  it('should return the error message when given', () => {
    const err = new TransformerError('an error occurred')
    expect(err.message).to.equal('an error occurred')
  })

  it('should return the error type when given', () => {
    const err = new TransformerError('an error occurred', { type: 'internal-error' })
    expect(err.type).to.equal('internal-error')
  })

  it('should return the statusCode when given', () => {
    const err = new TransformerError('an error occurred', { statusCode: 500 })
    expect(err.statusCode).to.equal(500)
  })

  it('should return the debugInfo when given', () => {
    const err = new TransformerError('an error occurred', { debugInfo: 'schemaFetch is not a function' })
    expect(err.debugInfo).to.equal('schemaFetch is not a function')
  })

  it('should return the constructor name assigned', () => {
    const err = new TransformerError('an error occurred')
    expect(err.name).to.equal('TransformerError')
  })
})
