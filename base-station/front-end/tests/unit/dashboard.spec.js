import Vuex from 'vuex'
import { shallowMount } from '@vue/test-utils'
import Dashboard from './../../src/views/Dashboard.vue'
import { storeConfig } from './../../src/store/index.js'

describe('Dashboard.vue', () => {
  let wrapper

  beforeEach(() => {
    const store = new Vuex.Store(storeConfig)
    wrapper = shallowMount(Dashboard, {
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
