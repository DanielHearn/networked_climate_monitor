<template>
  <main-panel>
    <template slot="content">
      <div class="content-column">
        <h1 class="title">Climate Monitor</h1>
        <h2 class="heading">Login</h2>
        <p class="text">Enter an email and password to login.</p>
        <form id="login" class="form" @submit="checkLogin" method="post">
          <div class="input-box">
            <p class="text">Email</p>
            <input
              type="email"
              class="input--text"
              name="email"
              v-model="email"
              placeholder="Email"
              tabindex="0"
            />
          </div>
          <div class="input-box">
            <p class="text">Password</p>
            <input
              type="password"
              class="input--text"
              name="password"
              v-model="password"
              placeholder="Password"
              tabindex="0"
            />
          </div>
          <router-link to="/reset-password" class="link" tabindex="-1"
            >Forgotten your password? Click here</router-link
          >
          <error-list
            v-if="errors.length"
            title="Errors:"
            v-bind:errors="errors"
          />
          <v-button
            :hierachyLevel="'primary'"
            :text="'Login'"
            type="submit"
            value="Submit"
            tabindex="0"
          />
          <router-link to="/register" class="link"
            >Not registered? Click here to register</router-link
          >
        </form>
      </div>
    </template>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import ErrorList from './../components/ErrorList/ErrorList.vue'
import { HTTP } from './../static/http-common'
import { processErrors } from './../static/helpers'
import {
  setStoredAccessToken,
  setStoredRefreshToken
} from './../store/storage.js'
import vButton from './../components/vButton/vButton.vue'

export default {
  name: 'login',
  components: {
    MainPanel,
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
      HTTP.post('login', {
        email: email,
        password: password
      })
        .then(response => {
          const data = response.data
          if (data.status && data.access_token && data.refresh_token) {
            const user = this.$store.state.user
            user.logged_in = true
            user.access_token = data.access_token
            user.refresh_token = data.refresh_token
            user.email = email
            user.user_id = 1

            setStoredAccessToken(data.access_token)
            setStoredRefreshToken(data.refresh_token)

            HTTP.get('account', {
              headers: { Authorization: 'Bearer ' + data.access_token }
            })
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
                console.log(e)
              })

            this.$store.commit('setUser', user)
            this.$toasted.show('Logged in')

            this.$router.push('/dashboard')
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

      if (valid) {
        this.login(email, password)
      }
    }
  }
}
</script>
