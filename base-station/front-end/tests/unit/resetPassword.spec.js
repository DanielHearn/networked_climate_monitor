import Vuex from 'vuex'
import { shallowMount } from '@vue/test-utils'
import ResetPassword from './../../src/views/ResetPassword.vue'
import { storeConfig } from './../../src/store/index.js'

describe('ResetPassword.vue', () => {
  let wrapper

  beforeEach(() => {
    const store = new Vuex.Store(storeConfig)
    wrapper = shallowMount(ResetPassword, {
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
})
