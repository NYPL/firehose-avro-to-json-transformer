const winston = require('winston')

// Set default NYPL agreed upon log levels
const levels = {
  emergency: 0,
  alert: 1,
  critical: 2,
  error: 3,
  warning: 4,
  notice: 5,
  info: 6,
  debug: 7
}

const getLogLevelCode = (levelString) => {
  switch (levelString) {
    case 'emergency':
      return 0
    case 'alert':
      return 1
    case 'critical':
      return 2
    case 'error':
      return 3
    case 'warning':
      return 4
    case 'notice':
      return 5
    case 'info':
      return 6
    case 'debug':
      return 7
    default:
      return 'n/a'
  }
}

const loggerTransports = []

if (process.env.NODE_ENV !== 'test') {
  loggerTransports.push(
    new winston.transports.Console({
      timestamp: () => {
        return new Date().toISOString()
      },
      formatter: (options) => {
        const result = {
          timestamp: options.timestamp(),
          levelCode: getLogLevelCode(options.level),
          level: options.level.toUpperCase()
        }

        if (process.pid) {
          result.pid = process.pid.toString()
        }

        if (options.message) {
          result.message = options.message
        }

        if (options.meta && Object.keys(options.meta).length) {
          if (options.meta && Object.keys(options.meta).length) {
            result.meta = JSON.stringify(options.meta)
          }
        }

        return JSON.stringify(result)
      }
    })
  )
}

const logger = new (winston.Logger)({
  levels: levels,
  transports: loggerTransports,
  exitOnError: false
})

module.exports = logger
