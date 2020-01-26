<template>
  <div
    id="app"
    :class="{
      'mobile-menu--active': $store.state.mobileMenu,
      mobile: $store.state.mobile
    }"
  >
    <v-nav></v-nav>
    <div class="mobile-menu" v-if="$store.state.mobileMenu">
      <ul @click="toggleMenu">
        <router-link to="/" class="link">Home</router-link>
        <router-link
          to="/login"
          v-if="!$store.state.user.logged_in"
          class="link"
          >Login</router-link
        >
        <router-link
          to="/register"
          v-if="!$store.state.user.logged_in"
          class="link"
          >Register</router-link
        >
        <router-link
          to="/dashboard"
          v-if="$store.state.user.logged_in"
          class="link"
          >Dashboard</router-link
        >
        <router-link
          to="/settings"
          v-if="$store.state.user.logged_in"
          class="link"
          >Settings</router-link
        >
      </ul>
    </div>
    <router-view :class="{ hidden: $store.state.mobileMenu }" />
  </div>
</template>

<style lang="scss">
@import './app.scss';
</style>

<script>
import { HTTP } from './static/http-common'
import { getStoredAccessToken, getStoredRefreshToken } from './store/storage.js'

import vNav from './components/Nav/Nav.vue'

export default {
  name: 'app',
  components: {
    vNav
  },
  methods: {
    checkScreenSize: function() {
      this.$store.commit('setMobile', window.innerWidth <= 800)
    }
  },
  created: function() {
    this.checkScreenSize()
    window.addEventListener('resize', this.checkScreenSize)

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
            user.settings = JSON.parse(data.account.settings.replace(/'/g, '"'))

            this.$store.commit('setUser', user)

            this.$toasted.show('Logged in')
          }
        })
        .catch(e => {
          if (e.response) {
            this.$toasted.show('Stored account credentials are invalid')
          } else if (e.request) {
            this.$toasted.show('Error contacting server')
          }
        })
    }
  }
}
</script>
