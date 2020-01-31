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
      const password = this.newPassword
      const newPassword = this.confirmPassword
      let valid = true

      if (resetToken === '') {
        this.errors.push('Enter a reset token.')
        valid = false
      }
      if (password === '') {
        this.errors.push('Enter a password.')
        valid = false
      } else if (password.length < 8 || password.length > 40) {
        this.errors.push('Password must be between 8 and 40 characters long.')
        valid = false
      }

      if (password !== newPassword) {
        this.errors.push('Password and confirm password be identical.')
        valid = false
      }

      if (valid) {
        this.resetPassword(resetToken, password)
      }
    },
    resetPassword: function(resetToken, password) {
      this.$toasted.show('Sending change request')

      changePassword(resetToken, password)
        .then(response => {
          const data = response.data
          if (data.status && data.new_reset_token) {
            const user = this.$store.state.user
            this.newResetToken = data.new_reset_token
            user.reset_token = data.new_reset_token

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
    if (this.$store.state.user.reset_token) {
      this.resetToken = this.$store.state.user.reset_token
    }
  }
}
