import ErrorList from './../ErrorList/ErrorList.vue'
import { register, getAccount } from './../../static/api'
import { processErrors } from './../../static/helpers'
import {
  setStoredAccessToken,
  setStoredRefreshToken
} from './../../store/storage.js'
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
      const newPassword = this.confirmPassword
      let valid = true

      if (email === '') {
        this.errors.push('Enter a email.')
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

      if (password !== newPassword) {
        this.errors.push('Password and confirm password be identical.')
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
            const user = this.$store.state.user
            user.logged_in = true
            user.access_token = data.access_token
            user.refresh_token = data.refresh_token
            user.email = email

            setStoredAccessToken(data.access_token)
            setStoredRefreshToken(data.refresh_token)

            getAccount(data.access_token)
              .then(response => {
                const data = response.data
                if (data.status && data.account) {
                  const user = this.$store.state.user
                  user.settings = JSON.parse(
                    data.account.settings.replace(/'/g, '"')
                  )

                  this.$store.commit('setUser', user)
                }
              })
              .catch(e => {
                console.warn(e)
              })

            this.$store.commit('setUser', user)
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
