import { HTTP } from './http-common'

/**
 * Get account details from API
 * @param {string} accessToken - User's access token
 */
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

/**
 * Update account details in API
 * @param {string} accessToken - User access token
 * @param {object} data - Updated user data
 */
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

/**
 * Attempt user login with API
 * @param {string} email - User's email
 * @param {string} password - User's password
 */
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

/**
 * Attempt user registration with API
 * @param {string} email - User's email
 * @param {string} password - User's password
 */
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

/**
 * Change the user's password
 * @param {string} resetToken - User's reset token
 * @param {string} password - User's password
 */
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

/**
 * Blacklist the access token from future logins
 * @param {string} accessToken - User's access token
 */
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

/**
 * Blacklist the refresh token from future logins
 * @param {string} accessToken - User's access token
 */
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

/**
 * Update sensor details in API
 * @param {string} accessToken - User's acess token
 * @param {number} sensorID - Sensor ID
 * @param {object} data - Updated sensor data
 */
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

/**
 * Get climate data for a specified sensor ID from the API
 * @param {string} accessToken - User's access token
 * @param {number} sensorID - Sensor ID
 * @param {number} quantity - Quantity of climate data points to be retrieved
 * @param {date} rangeStart - Start date of the time period
 * @param {date} rangeEnd - End date of the time period
 */
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

/**
 * Delete the specified sensor using its sensor ID
 * @param {string} accessToken - User's access token
 * @param {number} sensorID - Sensor ID
 */
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

/**
 * Delete the climate data from the specified sensor using its sensor ID
 * @param {string} accessToken - User's access token
 * @param {number} sensorID - Sensor ID
 */
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

/**
 * Get all sensors from the API
 * @param {string} accessToken - User's access token
 */
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
