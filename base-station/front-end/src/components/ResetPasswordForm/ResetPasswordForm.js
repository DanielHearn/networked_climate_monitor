import ErrorList from './../ErrorList/ErrorList.vue'
import { changePassword } from './../../static/api'
import { processErrors } from './../../static/helpers'
import vButton from './../vButton/vButton.vue'

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
    checkResetPassword: function(e) {
      e.preventDefault()
      this.errors = []
      this.newResetToken = ''

      const resetToken = this.resetToken
      const newPassword = this.newPassword
      const confirmPassword = this.confirmPassword
      let valid = true

      if (resetToken === '') {
        this.errors.push('Enter the reset token.')
        valid = false
      }
      if (newPassword === '') {
        this.errors.push('Enter a password.')
        valid = false
      } else if (newPassword.length < 8 || newPassword.length > 40) {
        this.errors.push('Password must be between 8 and 40 characters long.')
        valid = false
      }

      if (confirmPassword === '') {
        this.errors.push('Enter the password again to confirm.')
        valid = false
      } else if (newPassword !== confirmPassword) {
        this.errors.push('Password and confirm password should be identical.')
        valid = false
      }

      if (valid) {
        this.resetPassword(resetToken, newPassword)
      }
    },
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
    if (this.currentResetToken) {
      this.resetToken = this.currentResetToken
    }
  }
}
