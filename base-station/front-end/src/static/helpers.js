/**
 * Capitalises the first word of the string
 * @param {string} s - String to be capitalised
 */
export const capitalise = s => {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

/**
 * Converts a temperature value from celsius to the specified unit
 * @param {number} value - Temperature value
 * @param {number} unit - Temperature measurement unit
 */
export const convertTemperature = (value, unit) => {
  let convertedValue = value
  if (unit === 'f') {
    convertedValue = value * 1.8 + 32
  }
  convertedValue = convertedValue.toFixed(2)
  convertedValue = parseFloat(convertedValue, 10)
  return convertedValue
}

/**
 * Formats the input climate data into a formatted string
 * @param {number} type - Climate data type
 * @param {number} value - Climate data value
 * @param {number} unit - Climate data measurement unit
 */
export const formatClimateData = (type, value, unit) => {
  switch (type) {
    case 'Temperature':
      value = convertTemperature(value, unit)
      unit = `°${unit.toUpperCase()}`
  }

  return `${value}${unit}`
}

/**
 * Processes an array of strings or an object with strings into an array of errors
 * @param {array|object} errors - Array or object representing one or multiple errors
 */
export const processErrors = errors => {
  const outputErrors = []
  if (Array.isArray(errors)) {
    return errors
  } else if (typeof errors === 'object') {
    for (let errorField in errors) {
      const errorsForType = errors[errorField]
      for (let errorT in errorsForType) {
        const errorText = `${capitalise(errorField.replace(/_/g, ' '))}: ${
          errorsForType[errorT]
        }`
        outputErrors.push(errorText)
      }
    }
  }
  return outputErrors
}

/**
 * Gets the battery status text from the input voltage value
 * @param {number} voltage - Voltage value
 */
export const getBatteryStatusFromVoltage = voltage => {
  let status = 'Low'
  if (voltage >= 4.1) {
    status = 'High'
  } else if (voltage >= 3.8) {
    status = 'Medium'
  }
  return status
}
