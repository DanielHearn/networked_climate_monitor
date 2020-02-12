import ErrorList from './../ErrorList/ErrorList.vue'
import { register } from './../../static/api'
import { processErrors } from './../../static/helpers'
import vButton from './../vButton/vButton.vue'

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
    checkRegister: function(e) {
      e.preventDefault()
      this.errors = []

      const email = this.email
      const password = this.password
      const confirmPassword = this.confirmPassword
      let valid = true

      if (email === '') {
        this.errors.push('Enter an email.')
        valid = false
      } else if (email.indexOf('@') === -1) {
        this.errors.push('Enter a valid email.')
        valid = false
      }
      if (password === '') {
        this.errors.push('Enter a password.')
        valid = false
      } else if (password.length < 8 || password.length > 40) {
        this.errors.push('Password must be between 8 and 40 characters long.')
        valid = false
      }

      if (confirmPassword === '') {
        this.errors.push('Enter the password again to confirm.')
        valid = false
      } else if (password !== confirmPassword) {
        this.errors.push('Password and confirm password should be identical.')
        valid = false
      }

      if (valid) {
        this.register(email, password)
      }
    },
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
