import ErrorList from './../ErrorList/ErrorList.vue'
import { register } from './../../static/api'
import { processErrors } from './../../static/helpers'
import vButton from './../vButton/vButton.vue'

// Displays a register form with email, password, and confirm password inputs
export default {
  name: 'register-form',
  components: {
    ErrorList,
    vButton
  },
  data: function() {
    return {
      email: '',
      password: '',
      confirmPassword: '',
      errors: []
    }
  },
  methods: {
    // Validate form inputs and attempt register request if all inputs are valid
    checkRegister: function(e) {
      e.preventDefault()
      this.errors = []

      const email = this.email
      const password = this.password
      const confirmPassword = this.confirmPassword
      const numOfRequiredInputs = 3
      const validInputs = []

      if (email === '') {
        this.errors.push('Enter an email.')
      } else if (email.indexOf('@') === -1) {
        this.errors.push('Enter a valid email.')
      } else {
        validInputs.push('email')
      }

      if (password === '') {
        this.errors.push('Enter a password.')
      } else if (password.length < 8 || password.length > 40) {
        this.errors.push('Password must be between 8 and 40 characters long.')
      } else {
        validInputs.push('password')
      }

      if (confirmPassword === '') {
        this.errors.push('Enter the password again to confirm.')
      } else if (password !== confirmPassword) {
        this.errors.push('Password and confirm password should be identical.')
      } else {
        validInputs.push('confirm_password')
      }

      if (numOfRequiredInputs === validInputs.length) {
        this.register(email, password)
      }
    },
    // Send register request to API and update user state if request is valid
    register: function(email, password) {
      this.$toasted.show('Sending register request')

      register(email, password)
        .then(response => {
          const data = response.data
          if (data.status && data.access_token && data.refresh_token) {
            data.logged_in = true
            data.email = email

            this.$store.dispatch('register', data, true)
            this.$toasted.show('Registered')
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
  }
}
