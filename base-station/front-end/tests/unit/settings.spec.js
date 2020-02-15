import Vuex from 'vuex'
import { shallowMount } from '@vue/test-utils'
import Settings from './../../src/views/Settings.vue'
import { storeConfig } from './../../src/store/index.js'

describe('Login.vue', () => {
  let wrapper

  beforeEach(() => {
    const store = new Vuex.Store(storeConfig)
    wrapper = shallowMount(Settings, {
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
