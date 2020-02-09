import { mutations, actions } from './../../src/store/index.js'
import cloneDeep from 'lodash'

const { setMobile, setMobileMenu, setUser } = mutations
const { logout } = actions
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

// helper for testing action with expected mutations
const testAction = (action, payload, state, expectedMutations, done) => {
  let count = 0

  // mock commit
  const commit = (type, payload) => {
    const mutation = expectedMutations[count]

    try {
      expect(type).toBe(mutation.type)
      if (payload) {
        expect(payload).toEqual(mutation.payload)
      }
    } catch (error) {
      done(error)
    }

    count++
    if (count >= expectedMutations.length) {
      done()
    }
  }

  // call the action with mocked store and arguments
  action({ commit, state }, payload)

  // check if no mutations should have been dispatched
  if (expectedMutations.length === 0) {
    expect(count).toBe(0)
    done()
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
  })

  it('logout', done => {
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
    testAction(logout, null, state, [{ type: 'setUser', payload: user }], done)
    expect(state.user).toEqual({
      access_token: '',
      refresh_token: '',
      logged_in: false,
      email: '',
      settings: {
        temperature_unit: 'c'
      }
    })
  })
})
