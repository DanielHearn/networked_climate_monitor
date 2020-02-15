import Vuex from 'vuex'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import MobileMenu from './../../src/components/MobileMenu/MobileMenu.vue'

const localVue = createLocalVue()
localVue.use(Vuex)

const mutations = {
  setMobileMenu: jest.fn()
}

describe('MobileMenu.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    store = new Vuex.Store({ mutations })
    wrapper = shallowMount(MobileMenu, {
      propsData: {
        loggedIn: false
      },
      stubs: ['router-link'],
      store,
      localVue
    })
  })

  afterEach(() => {
    wrapper.destroy()
    jest.resetAllMocks()
  })

  it('Logged In', async () => {
    wrapper.setProps({ loggedIn: true })
    expect(wrapper.element).toMatchSnapshot()
  })

  it('Mobile menu toggle', async () => {
    wrapper.find('ul').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mutations.setMobileMenu).toHaveBeenCalledTimes(1)
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
