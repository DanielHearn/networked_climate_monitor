export const capitalise = (s) => {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export const processErrors = (errors) => {
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

export const getBatteryStatusFromVoltage = (voltage) => {
  let status = 'Bad'
  if (voltage >= 4.1) {
    status = 'Good'
  } else if (voltage >= 3.8) {
    status = 'Ok'
  }
  return status
}