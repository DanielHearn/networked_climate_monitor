import { formatClimateData } from './../../static/helpers'

export default {
  name: 'recent-climate-data',
  props: {
    recentClimateData: {
      type: Array,
      default: [],
      required: true
    },
    temperatureUnit: {
      type: String,
      default: 'c',
      required: true
    }
  },
  computed: {
    climateData: function() {
      const recentClimateData = this.recentClimateData
      const climateData = []
      for (let data of recentClimateData) {
        const modifiedData = data
        if (data.type === 'Temperature') {
          modifiedData.unit = this.temperatureUnit
        }

        modifiedData.formattedText = formatClimateData(
          modifiedData.type,
          modifiedData.value,
          modifiedData.unit
        )
        climateData.push(modifiedData)
      }
      return climateData
    }
  }
}
