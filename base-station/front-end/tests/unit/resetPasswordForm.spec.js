import Vuex from 'vuex'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import ResetPasswordForm from './../../src/components/ResetPasswordForm/ResetPasswordForm.vue'
import { changePassword } from './../../src/static/api.js'

const localVue = createLocalVue()
localVue.use(Vuex)
jest.mock('./../../src/static/api.js')

const actions = {
  updateResetToken: jest.fn()
}

const $toasted = {
  show: jest.fn()
}

describe('ResetPasswordForm.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    store = new Vuex.Store({ actions })
    wrapper = shallowMount(ResetPasswordForm, {
      propsData: {
        currentResetToken: ''
      },
      mocks: {
        $toasted,
        changePassword: jest.fn()
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
        new_reset_token: '12345'
      }
    }
    changePassword.mockResolvedValueOnce(response)

    const token = '1234'
    const password = 'password'
    const confirmPassword = password

    const tokenInput = wrapper.find('input[name="resetToken"]')
    tokenInput.element.value = token
    tokenInput.trigger('input')

    const passwordInput = wrapper.find('input[name="newPassword"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.resetToken).toBe(token)
    expect(wrapper.vm.newPassword).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')
    expect($toasted.show).toHaveBeenCalledWith('Sending change request')
    await wrapper.vm.$nextTick()

    expect($toasted.show).toHaveBeenCalledWith('Password changed')
    expect(actions.updateResetToken).toHaveBeenCalledTimes(1)
    expect(wrapper.vm.errors).toEqual([])
    expect(wrapper.vm.newResetToken).toBe('12345')
  })

  it('Missing reset token', async () => {
    const password = 'password'
    const confirmPassword = password

    const passwordInput = wrapper.find('input[name="newPassword"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.resetToken).toBe('')
    expect(wrapper.vm.newPassword).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.updateResetToken).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter the reset token.'])
    expect(wrapper.vm.newResetToken).toEqual('')
  })

  it('Missing password', async () => {
    const token = '1234'
    const confirmPassword = '1234'

    const tokenInput = wrapper.find('input[name="resetToken"]')
    tokenInput.element.value = token
    tokenInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.resetToken).toBe(token)
    expect(wrapper.vm.newPassword).toBe('')
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.updateResetToken).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Enter a password.',
      'Password and confirm password should be identical.'
    ])
    expect(wrapper.vm.newResetToken).toEqual('')
  })

  it('Missing confirm password', async () => {
    const token = '1234'
    const password = 'password'

    const tokenInput = wrapper.find('input[name="resetToken"]')
    tokenInput.element.value = token
    tokenInput.trigger('input')

    const passwordInput = wrapper.find('input[name="newPassword"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    expect(wrapper.vm.resetToken).toBe(token)
    expect(wrapper.vm.newPassword).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe('')

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.updateResetToken).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual(['Enter the password again to confirm.'])
    expect(wrapper.vm.newResetToken).toEqual('')
  })

  it('Missing token, password and confirm password', async () => {
    expect(wrapper.vm.resetToken).toBe('')
    expect(wrapper.vm.newPassword).toBe('')
    expect(wrapper.vm.confirmPassword).toBe('')

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.updateResetToken).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Enter the reset token.',
      'Enter a password.',
      'Enter the password again to confirm.'
    ])
    expect(wrapper.vm.newResetToken).toEqual('')
  })

  it('Invalid password', async () => {
    const token = '1234'
    const password = 'pass'
    const confirmPassword = password

    const tokenInput = wrapper.find('input[name="resetToken"]')
    tokenInput.element.value = token
    tokenInput.trigger('input')

    const passwordInput = wrapper.find('input[name="newPassword"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.resetToken).toBe(token)
    expect(wrapper.vm.newPassword).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.updateResetToken).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Password must be between 8 and 40 characters long.'
    ])
    expect(wrapper.vm.newResetToken).toEqual('')
  })

  it('Password mismatch', async () => {
    const token = '1234'
    const password = 'password1'
    const confirmPassword = 'password2'

    const tokenInput = wrapper.find('input[name="resetToken"]')
    tokenInput.element.value = token
    tokenInput.trigger('input')

    const passwordInput = wrapper.find('input[name="newPassword"]')
    passwordInput.element.value = password
    passwordInput.trigger('input')

    const confirmPasswordInput = wrapper.find('input[name="confirmPassword"]')
    confirmPasswordInput.element.value = confirmPassword
    confirmPasswordInput.trigger('input')

    expect(wrapper.vm.resetToken).toBe(token)
    expect(wrapper.vm.newPassword).toBe(password)
    expect(wrapper.vm.confirmPassword).toBe(confirmPassword)

    wrapper.trigger('submit')

    await wrapper.vm.$nextTick()

    expect(actions.updateResetToken).toHaveBeenCalledTimes(0)
    expect(wrapper.vm.errors).toEqual([
      'Password and confirm password should be identical.'
    ])
    expect(wrapper.vm.newResetToken).toEqual('')
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
