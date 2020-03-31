import Vuex from 'vuex'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import LoginForm from './../../src/components/LoginForm/LoginForm.vue'
import { login } from './../../src/static/api.js'

const localVue = createLocalVue()
localVue.use(Vuex)
jest.mock('./../../src/static/api.js')

const actions = {
  login: jest.fn()
}

describe('LoginForm.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    store = new Vuex.Store({ actions })
    wrapper = shallowMount(LoginForm, {
      mocks: {
        $toasted: {
          show: jest.fn()
        },
        login: jest.fn()
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

  it('Success', async () => {
    const response = {
      data: {
        status: 'Success',
        access_token: '1234',
        refresh_token: '1234',
        email: 'email@email.com',
        settings: '{"test": ""}'
      }
    }
    login.mockResolvedValueOnce(response)

    const email = 'email@email.com'
    const password = 'password'

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe(password)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()
    console.log(wrapper.html())
    expect(actions.login).toHaveBeenCalledTimes(1)
    expect(wrapper.vm.errors).toEqual([])
  })

  it('Missing email', async () => {
    const password = 'password'

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    expect(wrapper.vm.email).toBe('')
    expect(wrapper.vm.password).toBe(password)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.login).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter an email.'])
  })

  it('Missing password', async () => {
    const email = 'email@email.com'

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe('')

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.login).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter a password.'])
  })

  it('Missing email and password', async () => {
    expect(wrapper.vm.email).toBe('')
    expect(wrapper.vm.password).toBe('')

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.login).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter an email.', 'Enter a password.'])
  })

  it('Invalid email', async () => {
    const email = 'email.com'
    const password = 'password'

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe(password)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.login).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter a valid email.'])
  })

  it('Invalid password', async () => {
    const email = 'email@email.com'
    const password = 'pass'

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe(password)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.login).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Password must be between 8 and 40 characters long.'
    ])
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
