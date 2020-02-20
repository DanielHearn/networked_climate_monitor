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
    previousClimateData: {
      type: Array,
      default: () => {
        return []
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
          modifiedData.oneDayHigh = formatClimateData(
            modifiedData.type,
            this.trends[lowercaseType]['1_day']['high'],
            modifiedData.unit
          )
          modifiedData.oneDayLow = formatClimateData(
            modifiedData.type,
            this.trends[lowercaseType]['1_day']['low'],
            modifiedData.unit
          )
        }

        if (this.previousClimateData) {
          const previousData = this.previousClimateData.filter(
            climateData => climateData.type === data.type
          )[0]
          if (previousData) {
            const previousValue = previousData.value
            if (previousValue > data.value) {
              modifiedData.trendDirection = 'Down'
              modifiedData.trendDirectionIcon = 'arrow_downward'
            } else {
              modifiedData.trendDirection = 'Up'
              modifiedData.trendDirectionIcon = 'arrow_upward'
            }
            modifiedData.previousValue = formatClimateData(
              modifiedData.type,
              Math.abs(previousValue - data.value),
              modifiedData.unit
            )
          }
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
