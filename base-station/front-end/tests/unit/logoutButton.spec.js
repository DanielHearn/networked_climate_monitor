import { mount, createLocalVue, shallowMount } from '@vue/test-utils'
import Vuex from 'vuex'
import { storeConfig } from './../../src/store/index.js'
import LogoutButton from './../../src/components/LogoutButton/LogoutButton.vue'

describe('LogoutButton', () => {
  let wrapper
  let store
  const localVue = createLocalVue()
  localVue.use(Vuex)

  beforeEach(() => {
    store = new Vuex.Store(storeConfig)
    wrapper = shallowMount(LogoutButton, {
      store,
      localVue
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
  /*
  it('logout', () => {
    store.commit('setUser', {
      access_token: '1234',
      refresh_token: '1234',
      logged_in: true,
      email: 'email@email.com',
      settings: {
        temperature_unit: 'c'
      }
    })
    expect(store.state.user.logged_in).toBe(true)
    wrapper.vm.logout()
    expect(store.state.user.logged_in).toBe(false)
    expect(store.state.user.access_token).toBe('')
    expect(store.state.user.refresh_token).toBe('')
  })*/

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
