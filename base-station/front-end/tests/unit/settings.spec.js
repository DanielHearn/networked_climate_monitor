import Vuex from 'vuex'
import { mount, createLocalVue } from '@vue/test-utils'
import Settings from './../../src/views/Settings.vue'
import { storeConfig } from './../../src/store/index.js'
import { patchAccount, getAccount } from './../../src/static/api.js'
import { cloneDeep } from 'lodash'

const localVue = createLocalVue()
localVue.use(Vuex)
jest.mock('./../../src/static/api.js')

let wrapper
let store

const accountData = {
  status: 'Account successfully retrieved',
  account: {
    settings: '{\'temperature_unit\': \'c\'}',
    id: 1,
    reset_token: '1234',
    email: 'email@email.com'
  }
}

const patchAccountData = {
  status: 'Account successfully updated'
}

const factory = () => {
  store = new Vuex.Store(storeConfig)
  store.state.user.logged_in = true
  store.state.user.access_token = '1234'
  store.state.user.refresh_token = '1234'
  store.state.user.reset_token = '1234'
  store.state.user.email = 'email@email.com'
  store.state.user.settings = {
    temperature_unit: 'c'
  }

  return mount(Settings, {
    mocks: {
      $toasted: {
        show: jest.fn()
      },
      $router: {
        push: jest.fn()
      },
      patchAccount,
      getAccount
    },
    store,
    localVue
  })
}

describe('Settings.vue', () => {
  beforeEach(() => {
    wrapper = null
  })

  afterEach(() => {
    wrapper.destroy()
    jest.resetAllMocks()
  })

  it('has the expected html structure', async () => {
    const accountResponse = cloneDeep(accountData)
    getAccount.mockResolvedValueOnce(accountResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.element).toMatchSnapshot()
  })

  it('category changing', async () => {
    const accountResponse = cloneDeep(accountData)
    getAccount.mockResolvedValueOnce(accountResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    let activeCategoryListItem = wrapper.find('.side-panel .list-item.active')
    expect(activeCategoryListItem.find('.heading').text()).toBe(
      'Measurement Settings'
    )
    expect(wrapper.vm.activeCategoryID).toBe(0)
    wrapper
      .findAll('.side-panel .list-item')
      .at(1)
      .find('.actions .button')
      .trigger('click')

    await wrapper.vm.$nextTick()

    activeCategoryListItem = wrapper.find('.side-panel .list-item.active')
    expect(activeCategoryListItem.find('.heading').text()).toBe(
      'Account Management'
    )
    expect(wrapper.vm.activeCategoryID).toBe(1)

    expect(wrapper.element).toMatchSnapshot()
  })

  it('change temperature unit', async () => {
    const accountResponse = cloneDeep(accountData)
    getAccount.mockResolvedValueOnce(accountResponse)
    const patchResponse = cloneDeep(patchAccountData)
    patchAccount.mockResolvedValueOnce(patchResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.settings.temperature_unit).toBe('c')

    wrapper.find('label[for="temp_unit_f"]').trigger('click')

    const stringifiedSettings = JSON.stringify(wrapper.vm.settings)
    expect(wrapper.vm.settings.temperature_unit).toBe('f')
    expect(patchAccount).toBeCalledWith(store.state.user.access_token, {
      settings: stringifiedSettings
    })

    expect(wrapper.element).toMatchSnapshot()
  })

  it('reset token', async () => {
    const accountResponse = cloneDeep(accountData)
    getAccount.mockResolvedValueOnce(accountResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    wrapper
      .findAll('.side-panel .list-item')
      .at(1)
      .find('.actions .button')
      .trigger('click')
    expect(wrapper.vm.activeCategoryID).toBe(1)
    expect(wrapper.find('.settings-box span.bold').text()).toBe(
      store.state.user.reset_token
    )

    expect(wrapper.element).toMatchSnapshot()
  })
})
