import vButton from './../vButton/vButton.vue'
import { mapActions } from 'vuex'

// Displays the app's navigation bar
export default {
  name: 'v-nav',
  components: {
    vButton
  },
  props: {
    loggedIn: {
      type: Boolean,
      default: false,
      required: true
    },
    mobile: {
      type: Boolean,
      default: false,
      required: true
    },
    mobileMenu: {
      type: Boolean,
      default: false,
      required: true
    }
  },
  methods: {
    ...mapActions(['logout']),
    // Toggle mobile menu visibility
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
    }
  }
}
