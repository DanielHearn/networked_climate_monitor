import Vuex from 'vuex'
import { shallowMount } from '@vue/test-utils'
import Register from './../../src/views/Register.vue'
import { storeConfig } from './../../src/store/index.js'

describe('Register.vue', () => {
  let store
  let wrapper

  beforeEach(() => {
    store = new Vuex.Store(storeConfig)
    wrapper = shallowMount(Register, {
      stubs: ['router-link'],
      store
    })
  })

  afterEach(() => {
    wrapper.destroy()
    jest.resetAllMocks()
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })

  it('registered', () => {
    expect(wrapper.find('.register-success').exists()).toBe(false)
    store.state.user.email = 'email@email.com'
    expect(wrapper.find('.register-success').exists()).toBe(true)
    expect(wrapper.element).toMatchSnapshot()
  })
})
