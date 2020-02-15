import Vuex from 'vuex'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Nav from './../../src/components/Nav/Nav.vue'

const localVue = createLocalVue()
localVue.use(Vuex)

const mutations = {
  setMobileMenu: jest.fn()
}

describe('Nav.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    store = new Vuex.Store({ mutations })
    wrapper = shallowMount(Nav, {
      propsData: {
        mobile: false,
        mobileMenu: false,
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

  it('Desktop', async () => {
    expect(wrapper.find('.title--nav').exists()).toBe(true)
    expect(wrapper.find('.nav__links .link').exists()).toBe(true)
    expect(wrapper.find('.nav__links .link').text()).toBe('Home')
    expect(wrapper.find('.nav__right .logout-button').exists()).toBe(false)
    expect(wrapper.find('.nav__left .logout-button').exists()).toBe(false)
    expect(wrapper.find('.mobile-menu-button').exists()).toBe(false)

    wrapper.setProps({ loggedIn: true })
    expect(wrapper.find('.nav__right .logout-button').exists()).toBe(true)
    expect(wrapper.find('.nav__left .logout-button').exists()).toBe(false)
  })

  it('Mobile', async () => {
    wrapper.setProps({ mobile: true })
    expect(wrapper.find('.title--nav').exists()).toBe(false)
    expect(wrapper.find('.nav__links .link').exists()).toBe(false)

    expect(wrapper.find('.nav__right .logout-button').exists()).toBe(false)
    expect(wrapper.find('.nav__left .logout-button').exists()).toBe(false)

    expect(wrapper.find('.mobile-menu-button').exists()).toBe(true)

    wrapper.setProps({ loggedIn: true })
    expect(wrapper.find('.nav__right .logout-button').exists()).toBe(false)
    expect(wrapper.find('.nav__left .logout-button').exists()).toBe(true)
  })

  it('Mobile menu toggle', async () => {
    wrapper.setProps({ mobile: true })
    const menuButton = wrapper.find('.mobile-menu-button')
    expect(menuButton.exists()).toBe(true)
    expect(wrapper.find('.title--nav').exists()).toBe(false)
    menuButton.trigger('click')
    await wrapper.vm.$nextTick()
    expect(mutations.setMobileMenu).toHaveBeenCalledTimes(1)
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
