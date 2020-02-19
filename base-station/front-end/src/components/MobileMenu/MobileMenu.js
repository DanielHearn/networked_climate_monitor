// Displays a mobile menu
export default {
  name: 'mobile-menu',
  props: {
    loggedIn: {
      type: Boolean,
      default: false,
      required: true
    }
  },
  methods: {
    // Toggle mobile menu visibility
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
    }
  }
}
