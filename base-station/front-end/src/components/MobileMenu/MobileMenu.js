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
    toggleMenu: function() {
      this.$store.commit('setMobileMenu', !this.$store.state.mobileMenu)
    }
  }
}
