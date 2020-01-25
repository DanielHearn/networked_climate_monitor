export const capitalise = s => {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export const convertTemperature = (value, unit) => {
  let convertedValue = value
  if (unit === 'f') {
    convertedValue = value * 1.8 + 32
  }
  convertedValue = convertedValue.toFixed(2)
  convertedValue = parseFloat(convertedValue, 10)
  return convertedValue
}

export const formatClimateData = (type, value, unit) => {
  switch (type) {
    case 'Temperature':
      value = convertTemperature(value, unit)
      unit = `°${unit.toUpperCase()}`
  }

  return `${value}${unit}`
}

export const processErrors = errors => {
  const outputErrors = []
  if (Array.isArray(errors)) {
    for (let error of errors) {
      outputErrors.push(error)
    }
  } else if (typeof errors === 'object') {
    for (let errorField in errors) {
      const errorsForType = errors[errorField]
      for (let errorT in errorsForType) {
        const errorText = `${capitalise(errorField)}: ${errorsForType[errorT]}`
        outputErrors.push(errorText)
      }
    }
  }
  return outputErrors
}

export const getBatteryStatusFromVoltage = voltage => {
  let status = 'Low'
  if (voltage >= 4.1) {
    status = 'High'
  } else if (voltage >= 3.8) {
    status = 'Medium'
  }
  return status
}
