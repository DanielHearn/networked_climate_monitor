// Displays a list of errors within a red box
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
