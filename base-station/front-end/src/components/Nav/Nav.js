import vButton from './../vButton/vButton.vue'
import { mapActions } from 'vuex'

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
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
    }
  }
}
