import { formatClimateData } from './../../static/helpers'

// Displays a list of climate data
export default {
  name: 'recent-climate-data',
  props: {
    recentClimateData: {
      type: Array,
      default: [],
      required: true
    },
    trends: {
      type: Object,
      default: () => {
        return {}
      },
      required: false
    },
    temperatureUnit: {
      type: String,
      default: 'c',
      required: true
    }
  },
  computed: {
    // Format climate data
    climateData: function() {
      const recentClimateData = this.recentClimateData
      const climateData = []
      for (let data of recentClimateData) {
        const modifiedData = data
        const lowercaseType = data.type.toLowerCase()

        if (data.type === 'Temperature') {
          modifiedData.unit = this.temperatureUnit
        }

        if (this.trends && this.trends[lowercaseType]) {
          modifiedData.one_day_high = formatClimateData(
            modifiedData.type,
            this.trends[lowercaseType]['1_day']['high'],
            modifiedData.unit
          )
          modifiedData.one_day_low = formatClimateData(
            modifiedData.type,
            this.trends[lowercaseType]['1_day']['low'],
            modifiedData.unit
          )
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
