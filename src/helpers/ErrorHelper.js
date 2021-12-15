export default class TransformerError extends Error {
  constructor (message, opts = {}) {
    if (!message || typeof message !== 'string' || message.trim() === '') {
      throw new Error('an error message is required')
    }

    super(message)

    // Capturing stack trace, excluding constructor call from it.
    if (typeof Error.captureStackTrace === 'function') {
      Error.captureStackTrace(this, this.constructor)
    } else {
      this.stack = (new Error(message)).stack
    }

    // Saving class name in the property of our custom error as a shortcut.
    this.name = this.constructor.name

    if (opts.type) {
      this.type = opts.type
    }

    if (opts.statusCode) {
      this.statusCode = opts.statusCode
    }

    if (opts.debugInfo) {
      this.debugInfo = opts.debugInfo
    }
  }
}
