import { Line, mixins } from 'vue-chartjs'
const { reactiveProp } = mixins

// Displays a line chart
export default {
  extends: Line,
  mixins: [reactiveProp],
  props: ['options'],
  mounted() {
    // Render chart using chart data and options bound to component
    this.renderChart(this.chartData, this.options)
  }
}
