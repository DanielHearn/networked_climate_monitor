import { HTTP } from '../../static/http-common'
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
  computed: {
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

      HTTP.post(
        'logout/access',
        {},
        {
          headers: { Authorization: 'Bearer ' + accessToken }
        }
      )
        .then(() => {})
        .catch(e => {
          console.warn(e.response)
        })

      HTTP.post(
        'logout/refresh',
        {},
        {
          headers: { Authorization: 'Bearer ' + refreshToken }
        }
      )
        .then(() => {})
        .catch(e => {
          console.warn(e.response)
        })
    },
  }
}
