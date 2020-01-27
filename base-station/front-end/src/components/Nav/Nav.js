import vButton from './../vButton/vButton.vue'
import LogoutButton from './../LogoutButton/LogoutButton.vue'

export default {
  name: 'v-nav',
  components: {
    vButton,
    LogoutButton
  },
  methods: {
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
    }
  }
}
