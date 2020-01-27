<template>
  <div
    id="app"
    :class="{
      'mobile-menu--active': $store.state.mobileMenu,
      mobile: $store.state.mobile
    }"
  >
    <v-nav></v-nav>
    <mobile-menu v-if="$store.state.mobileMenu" />
    <router-view :class="{ hidden: $store.state.mobileMenu }" />
  </div>
</template>

<style lang="scss">
@import './app.scss';
</style>

<script>
// Helper imports
import { HTTP } from './static/http-common'
import { getStoredAccessToken, getStoredRefreshToken } from './store/storage.js'

// Component imports
import vNav from './components/Nav/Nav.vue'
import MobileMenu from './components/MobileMenu/MobileMenu.vue'

export default {
  name: 'app',
  components: {
    vNav,
    MobileMenu
  },
  methods: {
    checkScreenSize: function() {
      // Update mobile state if the browser's window with is below threshold
      this.$store.commit('setMobile', window.innerWidth <= 800)
    },
    loginFromStorage: function() {
      // Retrieve the tokens from local storage
      const accessToken = getStoredAccessToken()
      const refreshToken = getStoredRefreshToken()

      // If an access token exists then the user has previously logged in
      // so check if the access token is still valid
      if (accessToken) {
        HTTP.get('account', {
          headers: { Authorization: 'Bearer ' + accessToken }
        })
          .then(response => {
            const data = response.data
            // Access token is valid as the request was succesful so load the user data
            if (data.status && data.account) {
              // Create a local copy of the user to use in updating the user state
              const user = Object.assign({}, this.$store.state.user)
              user.logged_in = true
              user.access_token = accessToken
              user.refresh_token = refreshToken
              user.email = data.account.email

              // Parse the settings json data from a string
              user.settings = JSON.parse(
                data.account.settings.replace(/'/g, '"')
              )

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
  },
  created: function() {
    // Attempt to login from access token in local storage
    this.loginFromStorage()

    // Check the screen size to determine if the device is a mobile device
    this.checkScreenSize()

    // Assign an event listener to check screen size on resize if the user resizes the window
    window.addEventListener('resize', this.checkScreenSize)
  }
}
</script>
