import { mutations } from './../../src/store/index.js'
import cloneDeep from 'lodash'
import { fields, localStorage } from './../../src/store/storage.js'

const { setMobile, setMobileMenu, setUser } = mutations
const defaultState = {
  mobile: false,
  mobileMenu: false,
  user: {
    access_token: '',
    refresh_token: '',
    logged_in: false,
    email: '',
    settings: {}
  }
}

describe('store', () => {
  it('set mobile to true', () => {
    const state = cloneDeep(defaultState)

    setMobile(state, true)

    expect(state.mobile).toEqual(true)
  })

  it('set mobile to false', () => {
    const state = cloneDeep(defaultState)

    setMobile(state, false)

    expect(state.mobile).toEqual(false)
  })

  it('set mobileMenu to true', () => {
    const state = cloneDeep(defaultState)

    setMobileMenu(state, true)

    expect(state.mobileMenu).toEqual(true)
  })

  it('set mobileMenu to false', () => {
    const state = cloneDeep(defaultState)

    setMobileMenu(state, false)

    expect(state.mobileMenu).toEqual(false)
  })

  it('set user', () => {
    const state = cloneDeep(defaultState)
    const user = {
      access_token: 'access1234',
      refresh_token: 'refresh1234',
      logged_in: true,
      email: 'email@email.com',
      settings: {
        temperature_unit: 'c'
      }
    }

    setUser(state, user)

    expect(state.user).toEqual(user)
    expect(JSON.parse(localStorage.getItem(fields.access_token))).toBe(
      user.access_token
    )
    expect(JSON.parse(localStorage.getItem(fields.refresh_token))).toBe(
      user.refresh_token
    )
  })
})
