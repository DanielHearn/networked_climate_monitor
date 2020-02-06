import {
  getStoredAccessToken,
  setStoredAccessToken,
  getStoredRefreshToken,
  setStoredRefreshToken,
  fields,
  localStorage
} from './../../src/store/storage.js'

describe('storage', () => {
  it('getStoredAccessToken', () => {
    const token = 'test1234'
    expect(getStoredAccessToken()).toBe(null)
    localStorage.setItem(fields.access_token, JSON.stringify(token))
    expect(getStoredAccessToken()).toBe(token)
  })

  it('getStoredRefreshToken', () => {
    const token = 'test1234'
    expect(getStoredRefreshToken()).toBe(null)
    localStorage.setItem(fields.refresh_token, JSON.stringify(token))
    expect(getStoredRefreshToken()).toBe(token)
  })

  it('setStoredAccessToken', () => {
    const token = 'test1234'
    setStoredAccessToken(token)
    expect(JSON.parse(localStorage.getItem(fields.access_token))).toBe(token)

    setStoredAccessToken('')
    expect(JSON.parse(localStorage.getItem(fields.access_token))).toBe('')
  })

  it('setStoredRefreshToken', () => {
    const token = 'test1234'
    setStoredRefreshToken(token)
    expect(JSON.parse(localStorage.getItem(fields.refresh_token))).toBe(token)

    setStoredRefreshToken('')
    expect(JSON.parse(localStorage.getItem(fields.refresh_token))).toBe('')
  })
})
