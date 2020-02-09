import vButton from './../vButton/vButton.vue'
import { mapActions } from 'vuex'

export default {
  name: 'v-nav',
  components: {
    vButton
  },
  methods: {
    ...mapActions(['logout']),
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
    }
  }
}
