export const fields = {
  access_token: 'access_token',
  refresh_token: 'refresh_token'
}

export const localStorage = window.localStorage

/**
 * Get the access token from local storage
 */
export const getStoredAccessToken = function() {
  return JSON.parse(localStorage.getItem(fields.access_token))
}

/**
 * Get the refresh token from local storage
 */
export const getStoredRefreshToken = function() {
  return JSON.parse(localStorage.getItem(fields.refresh_token))
}

/**
 * Store the input access token into the local storage
 * @param {string} accessToken - User's access token
 */
export const setStoredAccessToken = function(accessToken) {
  localStorage.setItem(fields.access_token, JSON.stringify(accessToken))
}

/**
 * Store the input refresh token into the local storage
 * @param {string} refreshToken - User's refresh token
 */
export const setStoredRefreshToken = function(refreshToken) {
  localStorage.setItem(fields.refresh_token, JSON.stringify(refreshToken))
}
