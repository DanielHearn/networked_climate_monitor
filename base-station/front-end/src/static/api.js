import { HTTP } from './http-common'

export const getAccount = accessToken => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.get('account', {
      headers: { Authorization: 'Bearer ' + accessToken }
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const patchAccount = (accessToken, data) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.patch('account', data, {
      headers: { Authorization: 'Bearer ' + accessToken }
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const login = (email, password) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.post('login', {
      email: email,
      password: password
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const register = (email, password) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.post('account', {
      email: email,
      password: password
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const changePassword = (resetToken, password) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.post('accounts/actions/change-password', {
      reset_token: resetToken,
      password: password
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const logoutAccessToken = accessToken => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.post(
      'logout/access',
      {},
      {
        headers: { Authorization: 'Bearer ' + accessToken }
      }
    )
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const logoutRefreshToken = accessToken => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.post(
      'logout/refresh',
      {},
      {
        headers: { Authorization: 'Bearer ' + accessToken }
      }
    )
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const patchSensor = (accessToken, sensorID, data) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.patch(`sensors/${sensorID}`, data, {
      headers: { Authorization: 'Bearer ' + accessToken }
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const getClimateData = (
  accessToken,
  sensorID,
  quantity,
  rangeStart,
  rangeEnd
) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.get(
      `sensors/${sensorID}/climate-data?range_start=${rangeStart}&range_end=${rangeEnd}`,
      {
        headers: { Authorization: 'Bearer ' + accessToken }
      }
    )
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const deleteSensor = (accessToken, sensorID) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.delete(`sensors/${sensorID}`, {
      headers: { Authorization: 'Bearer ' + accessToken }
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const deleteClimateData = (accessToken, sensorID) => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.delete(`sensors/${sensorID}/climate-data`, {
      headers: { Authorization: 'Bearer ' + accessToken }
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}

export const getSensors = accessToken => {
  const promise = new Promise(function(resolve, reject) {
    HTTP.get('sensors', {
      headers: { Authorization: 'Bearer ' + accessToken }
    })
      .then(response => {
        resolve(response)
      })
      .catch(e => {
        reject(e)
      })
  })
  return promise
}
