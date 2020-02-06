export const fields = {
  access_token: 'access_token',
  refresh_token: 'refresh_token'
}

export const localStorage = window.localStorage

// Getters
export const getStoredAccessToken = function() {
  return JSON.parse(localStorage.getItem(fields.access_token))
}

export const getStoredRefreshToken = function() {
  return JSON.parse(localStorage.getItem(fields.refresh_token))
}

// Setters
export const setStoredAccessToken = function(accessToken) {
  localStorage.setItem(fields.access_token, JSON.stringify(accessToken))
}

export const setStoredRefreshToken = function(refreshToken) {
  localStorage.setItem(fields.refresh_token, JSON.stringify(refreshToken))
}
