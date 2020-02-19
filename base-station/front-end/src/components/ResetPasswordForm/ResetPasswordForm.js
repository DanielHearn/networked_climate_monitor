import ErrorList from './../ErrorList/ErrorList.vue'
import { changePassword } from './../../static/api'
import { processErrors } from './../../static/helpers'
import vButton from './../vButton/vButton.vue'

// Displays a reset password form with reset token, new password, and confirm password inputs
export default {
  name: 'reset-password-form',
  components: {
    ErrorList,
    vButton
  },
  props: {
    currentResetToken: {
      type: String,
      default: '',
      required: false
    }
  },
  data: function() {
    return {
      resetToken: '',
      newPassword: '',
      confirmPassword: '',
      newResetToken: '',
      errors: []
    }
  },
  methods: {
    // Validate form inputs and attempt reset password request if all inputs are valid
    checkResetPassword: function(e) {
      e.preventDefault()
      this.errors = []
      this.newResetToken = ''

      const resetToken = this.resetToken
      const newPassword = this.newPassword
      const confirmPassword = this.confirmPassword
      const numOfRequiredInputs = 3
      const validInputs = []

      if (resetToken === '') {
        this.errors.push('Enter the reset token.')
      } else {
        validInputs.push('reset_token')
      }

      if (newPassword === '') {
        this.errors.push('Enter a password.')
      } else if (newPassword.length < 8 || newPassword.length > 40) {
        this.errors.push('Password must be between 8 and 40 characters long.')
      } else {
        validInputs.push('new_password')
      }

      if (confirmPassword === '') {
        this.errors.push('Enter the password again to confirm.')
      } else if (newPassword !== confirmPassword) {
        this.errors.push('Password and confirm password should be identical.')
      } else {
        validInputs.push('confirm_password')
      }

      if (numOfRequiredInputs === validInputs.length) {
        this.resetPassword(resetToken, newPassword)
      }
    },
    // Send reset password request to API and update user state if request is valid
    resetPassword: function(resetToken, password) {
      this.$toasted.show('Sending change request')

      changePassword(resetToken, password)
        .then(response => {
          const data = response.data
          if (data.status && data.new_reset_token) {
            this.newResetToken = data.new_reset_token
            this.$store.dispatch('updateResetToken', data.new_reset_token)

            this.newPassword = ''
            this.confirmPassword = ''
            this.resetToken = ''

            this.$toasted.show('Password changed')
          }
        })
        .catch(e => {
          if (e.response && e.response.data && e.response.data.errors) {
            this.errors = processErrors(e.response.data.errors)
          } else {
            this.errors.push(e)
          }
        })
    }
  },
  created: function() {
    // Prefill reset token with token from props
    if (this.currentResetToken) {
      this.resetToken = this.currentResetToken
    }
  }
}
