<template>
  <div
    id="app"
    :class="{
      'mobile-menu--active': $store.state.mobileMenu,
      mobile: $store.state.mobile
    }"
  >
    <div id="nav">
      <div class="nav__side">
        <router-link to="/" class="link title--nav" v-if="!$store.state.mobile"
          >Climate Monitor</router-link
        >
        <v-button
          v-else
          @click.native="logout"
          :type="'secondary'"
          :text="'person'"
          :isIcon="true"
        />
      </div>
      <div class="nav__links" v-if="!$store.state.mobile">
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
      </div>
      <div class="nav__side">
        <v-button
          v-if="$store.state.user.logged_in && !$store.state.mobile"
          @click.native="logout"
          :type="'secondary'"
          :text="'person'"
          :isIcon="true"
        />
        <v-button
          v-if="$store.state.mobile"
          @click.native="toggleMenu"
          :type="'secondary'"
          :text="$store.state.mobileMenu ? 'close' : 'menu'"
          :isIcon="true"
          style="margin-left: 2em;"
        />
      </div>
    </div>
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
    },
    checkScreenSize: function() {
      this.$store.commit('setMobile', window.innerWidth <= 800)
    },
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
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
