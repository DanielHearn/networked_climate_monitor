import { logoutAccessToken, logoutRefreshToken } from '../../static/api'
import {
  setStoredAccessToken,
  setStoredRefreshToken
} from '../../store/storage.js'
import vButton from './../vButton/vButton.vue'

export default {
  name: 'logout-button',
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
      this.$store.commit('setUser', user)

      setStoredAccessToken('')
      setStoredRefreshToken('')

      this.$toasted.show('Logged out')

      if (this.$route.name !== 'home') {
        this.$router.push('/')
      }

      logoutAccessToken(accessToken)
        .then(() => {})
        .catch(e => {
          console.warn(e.response)
        })

      logoutRefreshToken(refreshToken)
        .then(() => {})
        .catch(e => {
          console.warn(e.response)
        })
    }
  }
}
