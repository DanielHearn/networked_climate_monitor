export default {
  name: 'v-button',
  props: {
    type: {
      type: String,
      default: 'primary',
      required: true
    },
    text: {
      type: String,
      default: '',
      required: true
    },
    isIcon: {
      type: Boolean,
      default: false,
      required: false
    }
  },
  computed: {
    typeClass: function() {
      return `button--${this.type}`
    }
  }
}
