import ErrorList from './../ErrorList/ErrorList.vue'
import { login } from './../../static/api'
import { processErrors } from './../../static/helpers'
import vButton from './../vButton/vButton.vue'

// Displays a login form with email and password inputs
export default {
  name: 'login-form',
  components: {
    ErrorList,
    vButton
  },
  data: function() {
    return {
      email: '',
      password: '',
      errors: []
    }
  },
  methods: {
    // Send login request to API and update user state if request is valid
    login: function(email, password) {
      this.$toasted.show('Sending login request')

      login(email, password)
        .then(response => {
          const data = response.data
          if (data.status && data.access_token && data.refresh_token) {
            data.logged_in = true
            data.settings = JSON.parse(data.settings.replace(/'/g, '"'))
            this.$store.dispatch('login', data)
          }
        })
        .catch(e => {
          if (e.response && e.response.data && e.response.data.errors) {
            this.errors = processErrors(e.response.data.errors)
          } else {
            this.errors.push(e)
          }
        })
    },
    // Validate form inputs and attempt login request if all inputs are valid
    checkLogin: function(e) {
      e.preventDefault()
      this.errors = []
      const email = this.email
      const password = this.password
      const numOfRequiredInputs = 2
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

      if (numOfRequiredInputs === validInputs.length) {
        this.login(email, password)
      }
    }
  }
}
