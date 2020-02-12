import ErrorList from './../ErrorList/ErrorList.vue'
import { login } from './../../static/api'
import { processErrors } from './../../static/helpers'
import vButton from './../vButton/vButton.vue'

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
    login: function(email, password) {
      this.$toasted.show('Sending login request')
      login(email, password)
        .then(response => {
          const data = response.data
          if (data.status && data.access_token && data.refresh_token) {
            data.email = email
            data.logged_in = true
            this.$store.dispatch('login', data, true)
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
    checkLogin: function(e) {
      e.preventDefault()
      this.errors = []
      const email = this.email
      const password = this.password
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

      if (valid) {
        this.login(email, password)
      }
    }
  }
}
