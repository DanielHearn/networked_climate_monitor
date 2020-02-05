import {
  capitalise,
  convertTemperature,
  formatClimateData,
  processErrors,
  getBatteryStatusFromVoltage
} from './../../src/static/helpers.js'

describe('helpers', () => {
  it('getBatteryStatusFromVoltage', () => {
    expect(getBatteryStatusFromVoltage(4.2)).toBe('High')
    expect(getBatteryStatusFromVoltage(3.9)).toBe('Medium')
    expect(getBatteryStatusFromVoltage(3.7)).toBe('Low')
  })

  it('capitalise', () => {
    expect(capitalise('test')).toBe('Test')
    expect(capitalise('Test')).toBe('Test')
    expect(capitalise('TEST')).toBe('TEST')
    expect(() => {
      capitalise(123)
    }).toThrow()
    expect(() => {
      capitalise(true)
    }).toThrow()
  })

  it('convertTemperature', () => {
    expect(convertTemperature(24.23, 'c')).toBe(24.23)
    expect(convertTemperature(24.236272, 'c')).toBe(24.24)
    expect(convertTemperature(24.23, 'f')).toBe(75.61)
    expect(convertTemperature(24.237245, 'f')).toBe(75.63)
  })

  it('formatClimateData', () => {
    expect(formatClimateData('Humidity', 45.32, '%')).toBe('45.32%')
    expect(formatClimateData('Pressure', 1000.23, 'hPa')).toBe('1000.23hPa')
    expect(formatClimateData('Temperature', 24.23, 'c')).toBe('24.23°C')
    expect(formatClimateData('Temperature', 24.23, 'f')).toBe('75.61°F')
  })

  it('processErrors', () => {
    const errorArray = [
      'Password is not a string',
      'ID is not a integer',
      'Email field is missing'
    ]
    const errorObject = {
      password: ['is not a string', 'is not a valid password'],
      email: ['is not a string', 'is not a valid email']
    }

    expect(processErrors(errorArray)).toStrictEqual(errorArray)

    expect(processErrors(errorObject)).toStrictEqual([
      'Password: is not a string',
      'Password: is not a valid password',
      'Email: is not a string',
      'Email: is not a valid email'
    ])
  })
})
