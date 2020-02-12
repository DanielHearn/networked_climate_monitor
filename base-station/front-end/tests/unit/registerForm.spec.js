import Vuex from 'vuex'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import RegisterForm from './../../src/components/RegisterForm/RegisterForm.vue'
import { register } from './../../src/static/api.js'

const localVue = createLocalVue()
localVue.use(Vuex)
jest.mock('./../../src/static/api.js')

const actions = {
  register: jest.fn()
}

describe('RegisterForm.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    store = new Vuex.Store({ actions })
    wrapper = shallowMount(RegisterForm, {
      mocks: {
        $toasted: {
          show: jest.fn()
        },
        register: jest.fn()
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
        refresh_token: '1234'
      }
    }
    register.mockResolvedValueOnce(response)

    const email = 'email@email.com'
    const password = 'password'
    const confirmPassword = password

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(1)
    expect(wrapper.vm.errors).toEqual([])
  })

  it('Missing email', async () => {
    const password = 'password'
    const confirmPassword = password

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.email).toBe('')
    expect(wrapper.vm.password).toBe(password)
    expect(wrapper.vm.password).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter an email.'])
  })

  it('Missing password', async () => {
    const email = 'email@email.com'
    const confirmPassword = '1234'

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe('')
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Enter a password.',
      'Password and confirm password should be identical.'
    ])
  })

  it('Missing confirm password', async () => {
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
    expect(wrapper.vm.confirmPassword).toBe('')

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter the password again to confirm.'])
  })

  it('Missing email, password and confirm password', async () => {
    expect(wrapper.vm.email).toBe('')
    expect(wrapper.vm.password).toBe('')
    expect(wrapper.vm.confirmPassword).toBe('')

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Enter an email.',
      'Enter a password.',
      'Enter the password again to confirm.'
    ])
  })

  it('Invalid email', async () => {
    const email = 'email.com'
    const password = 'password'
    const confirmPassword = password

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter a valid email.'])
  })

  it('Invalid password', async () => {
    const email = 'email@email.com'
    const password = 'pass'
    const confirmPassword = password

    const emailInput = wrapper.find('input[name="email"]')
    emailInput.element.value = email
    emailInput.trigger('input')

    const passwordInput = wrapper.find('input[name="password"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.email).toBe(email)
    expect(wrapper.vm.password).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.register).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Password must be between 8 and 40 characters long.'
    ])
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
