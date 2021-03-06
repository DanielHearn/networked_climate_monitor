// Displays text or icon button
export default {
  name: 'v-button',
  props: {
    hierachyLevel: {
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
    // Generates the hierarchy class
    typeClass: function() {
      return `button--${this.hierachyLevel}`
    }
  }
}
