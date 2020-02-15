<template>
  <div
    id="app"
    :class="{
      'mobile-menu--active': $store.state.mobileMenu,
      mobile: $store.state.mobile
    }"
  >
    <v-nav
      :mobile="$store.state.mobile"
      :mobile-menu="$store.state.mobileMenu"
      :logged-in="$store.state.user.logged_in"
    ></v-nav>
    <mobile-menu
      v-if="$store.state.mobileMenu"
      :logged-in="$store.state.user.logged_in"
    />
    <router-view :class="{ hidden: $store.state.mobileMenu }" />
  </div>
</template>

<style lang="scss">
@import './app.scss';
</style>

<script>
// Helper imports
import {
  getAccount,
  logoutAccessToken,
  logoutRefreshToken
} from './static/api.js'
import {
  getStoredAccessToken,
  getStoredRefreshToken,
  setStoredAccessToken,
  setStoredRefreshToken
} from './store/storage.js'

// Component imports
import vNav from './components/Nav/Nav.vue'
import MobileMenu from './components/MobileMenu/MobileMenu.vue'
import { mapState } from 'vuex'

export default {
  name: 'app',
  components: {
    vNav,
    MobileMenu
  },
  computed: mapState(['user']),
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
        getAccount(accessToken)
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
              user.reset_token = data.account.reset_token
              user.settings = JSON.parse(
                data.account.settings.replace(/'/g, '"')
              )
              console.log(data.account.settings.replace(/'/g, '"'))

              this.$store.dispatch('login', user, false)
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

    this.$store.subscribeAction(action => {
      switch (action.type) {
        case 'register':
          setStoredAccessToken(action.payload.access_token)
          setStoredRefreshToken(action.payload.refresh_token)
          break
        case 'login':
          this.$toasted.show('Logged in')
          setStoredAccessToken(action.payload.access_token)
          setStoredRefreshToken(action.payload.refresh_token)

          if (this.$route.name === 'login' || this.$route.name === null) {
            this.$router.push({ name: 'dashboard' })
          }
          break
        case 'logout':
          this.$toasted.show('Logged out')
          if (this.$route.name !== 'home' || this.$route.name === null) {
            this.$router.push({ name: 'home' })
          }

          logoutAccessToken(getStoredAccessToken())
            .then(() => {})
            .catch(e => {
              console.warn(e.response)
            })

          logoutRefreshToken(getStoredRefreshToken())
            .then(() => {})
            .catch(e => {
              console.warn(e.response)
            })

          setStoredAccessToken('')
          setStoredRefreshToken('')
          break
      }
    })
  }
}
</script>
