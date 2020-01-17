<template>
  <div id="app">
    <div id="nav">
      <div class="nav__side">
        <p class="title--nav">Climate Monitor</p>
      </div>
      <div class="nav__links">
        <router-link to="/">Home</router-link>
        <router-link to="/login" v-if="!$store.state.user.logged_in"
          >Login</router-link
        >
        <router-link to="/register" v-if="!$store.state.user.logged_in"
          >Register</router-link
        >
        <router-link to="/dashboard" v-if="$store.state.user.logged_in"
          >Dashboard</router-link
        >
        <router-link to="/settings" v-if="$store.state.user.logged_in"
          >Settings</router-link
        >
      </div>
      <div class="nav__side">
        <v-button
          v-if="$store.state.user.logged_in"
          @click="logout"
          :type="'primary'"
          :text="'person'"
          :isIcon="true"
        />
      </div>
    </div>
    <router-view />
  </div>
</template>

<style lang="scss">
@import './app.scss';
</style>

<script>
import { HTTP } from './static/http-common'
import vButton from './components/vButton/vButton.vue'
import {
  getStoredAccessToken,
  getStoredRefreshToken,
  setStoredAccessToken,
  setStoredRefreshToken
} from './store/storage.js'

export default {
  name: 'app',
  components: {
    vButton
  },
  methods: {
    logout: function() {
      const user = this.$store.state.user
      const accessToken = user.access_token
      const refreshToken = user.refresh_token

      user.logged_in = false
      user.access_token = ''
      user.refresh_token = ''
      user.email = ''
      user.user_id = 0
      this.$store.commit('setUser', user)

      setStoredAccessToken('')
      setStoredRefreshToken('')

      this.$toasted.show('Logged out')

      if (this.$route.name !== 'home') {
        this.$router.push('/')
      }
      console.log(accessToken)
      HTTP.post(
        'logout/access',
        {},
        {
          headers: { Authorization: 'Bearer ' + accessToken }
        }
      )
        .then(response => {
          const data = response.data
          if (data.status) {
            console.log(data.status)
          }
        })
        .catch(e => {
          console.log(e.response)
        })

      HTTP.post(
        'logout/refresh',
        {},
        {
          headers: { Authorization: 'Bearer ' + refreshToken }
        }
      )
        .then(response => {
          const data = response.data
          if (data.status) {
            console.log(data.status)
          }
        })
        .catch(e => {
          console.log(e.response)
        })
    }
  },
  created: function() {
    const accessToken = getStoredAccessToken()
    const refreshToken = getStoredRefreshToken()

    if (accessToken) {
      HTTP.get('account', {
        headers: { Authorization: 'Bearer ' + accessToken }
      })
        .then(response => {
          const data = response.data
          if (data.status && data.account) {
            const user = this.$store.state.user
            user.logged_in = true
            user.access_token = accessToken
            user.refresh_token = refreshToken
            user.email = data.account.email
            user.user_id = data.account.id
            user.settings = JSON.parse(data.account.settings.replace(/'/g, '"'))

            this.$store.commit('setUser', user)

            this.$toasted.show('Logged in')
          }
        })
        .catch(e => {
          console.log(e.response)
        })
    }
  }
}
</script>
