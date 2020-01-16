export default {
  name: 'error-list',
  props: {
    title: {
      type: String,
      default: '',
      required: false
    },
    errors: {
      type: Array,
      default: [],
      required: true
    }
  }
}
