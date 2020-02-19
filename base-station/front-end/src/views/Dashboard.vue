<template>
  <div class="content">
    <side-panel
      v-if="
        !$store.state.mobile ||
          ($store.state.mobile && activeSensorIndex === -1)
      "
    >
      <template slot="header">
        <p class="sub-heading">Sensor Nodes</p>
        <v-button
          @click.native="refreshSensors"
          :hierachyLevel="'secondary'"
          :text="'refresh'"
          :isIcon="true"
        />
      </template>
      <template slot="content">
        <ul v-if="sensors.length" class="list">
          <li
            v-for="(sensor, index) in sensors"
            :key="index"
            class="list-item"
            v-bind:class="{ active: sensor.id === activeSensorID }"
            style="display: flex; flex-direction: column; justify-content: flex-start; text-align: left;"
          >
            <template v-if="sensor">
              <div class="edit-box">
                <p
                  class="heading"
                  :class="{
                    underline: sensor.id === activeSensorID
                  }"
                  v-if="!sensor.editing"
                >
                  Node {{ sensor.id }}: {{ sensor.name }}
                </p>
                <p
                  v-else
                  class="heading"
                  :class="{
                    underline: sensor.id === activeSensorID
                  }"
                >
                  Node {{ sensor.id }}:
                </p>
                <input
                  type="text"
                  class="input--text input--small"
                  v-model="sensor.name"
                  v-on:change="changeSensorName(sensor.id, sensor.name)"
                  :ref="`sensor_name_${sensor.id}`"
                  @blur="sensor.editing = false"
                  v-if="sensor.editing"
                />
                <v-button
                  @click.native="setSensorEditing(sensor.id)"
                  :hierachyLevel="sensor.editing ? 'primary' : 'tertiary'"
                  :text="'edit'"
                  :isIcon="true"
                />
              </div>
              <div v-if="sensor.recent_climate_data">
                <ul
                  style="list-style: none; padding: 0; margin-top: 0.5em; display: flex; flex-direction: row;"
                >
                  <li
                    v-for="(data, index) in sensor.recent_climate_data
                      .climate_data"
                    :key="index"
                    style="padding-right: 0.5em;"
                  >
                    <template v-if="data.type === 'Temperature'">
                      <p class="text text--bold" style="margin: 0.5em 0 0 0;">
                        {{ data.type }}:
                        {{
                          formatClimateData(
                            data.type,
                            data.value,
                            settings.temperature_unit
                          )
                        }}
                      </p>
                    </template>
                    <template v-if="data.type === 'Humidity'">
                      <p class="text text--bold" style="margin: 0.5em 0 0 0;">
                        {{ data.type }}: {{ data.value }}{{ data.unit }}
                      </p>
                    </template>
                  </li>
                </ul>
                <p class="text">
                  Date received: {{ sensor.recent_climate_data.date }}
                </p>
                <p
                  class="text"
                  style="display: flex;"
                  :class="
                    'battery-status--' +
                      getBatteryStatusFromVoltage(
                        sensor.recent_climate_data.battery_voltage
                      ).toLowerCase()
                  "
                >
                  Battery level:
                  {{
                    getBatteryStatusFromVoltage(
                      sensor.recent_climate_data.battery_voltage
                    )
                  }}
                  <i
                    v-if="sensor.recent_climate_data.battery_voltage < 3.9"
                    class="material-icons"
                    >battery_alert</i
                  >
                </p>
              </div>
              <div v-else>
                <p class="text">No climate data for this sensor</p>
              </div>
              <div class="actions">
                <v-button
                  @click.native="setSensorConfig(sensor.id)"
                  :hierachyLevel="'secondary'"
                  :text="sensor.config ? 'close' : 'settings'"
                  :isIcon="true"
                />
                <v-button
                  @click.native="setActiveSensor(sensor.id)"
                  :hierachyLevel="'primary'"
                  :text="'View Climate'"
                />
              </div>
              <div
                v-if="sensor.config"
                :class="['actions', { 'actions--active': sensor.config }]"
              >
                <v-button
                  @click.native="deleteSensor(sensor.id, sensor.name)"
                  :hierachyLevel="'tertiary'"
                  :text="'Delete Sensor'"
                />
                <v-button
                  @click.native="deleteClimate(sensor.id, sensor.name)"
                  :hierachyLevel="'tertiary'"
                  :text="'Delete Climate Data'"
                />
              </div>
            </template>
          </li>
        </ul>
        <ul v-else class="list">
          <li class="list-item">
            <p class="text">
              No sensor nodes created. Connect a sensor node to the base station
              to create a new sensor.
            </p>
          </li>
        </ul>
      </template>
    </side-panel>
    <template
      v-if="
        !$store.state.mobile ||
          ($store.state.mobile && activeSensorIndex !== -1)
      "
    >
      <main-panel v-if="activeSensorIndex === -1">
        <template slot="header">
          <p class="sub-heading">Climate Data</p>
        </template>
        <template slot="content">
          <p class="heading">No sensor selected</p>
        </template>
      </main-panel>
      <main-panel v-else-if="activeSensor">
        <template slot="header">
          <p class="sub-heading">
            Node {{ activeSensor.id }}: {{ activeSensor.name }}
          </p>
          <v-button
            @click.native="refreshSensors"
            :hierachyLevel="'secondary'"
            :text="'refresh'"
            :isIcon="true"
          />
        </template>
        <template slot="content">
          <div class="dashboard-content">
            <v-button
              v-if="$store.state.mobile"
              @click.native="backToSensorList()"
              :hierachyLevel="'tertiary'"
              :text="'Back'"
              class="back-button"
            />
            <template v-if="activeSensor && activeSensor.recent_climate_data">
              <h3 class="heading">Recent Climate Data</h3>
              <p class="text">
                Date received:
                {{ activeSensor.recent_climate_data.date }}
              </p>
              <recent-climate-data
                :recent-climate-data="
                  activeSensor.recent_climate_data.climate_data
                "
                :temperature-unit="settings.temperature_unit"
              />

              <h3 class="heading">Historical Climate Data</h3>
              <div class="historical-actions">
                <div class="input-box">
                  <p class="text">Historical Date Range</p>
                  <v-date-picker
                    v-model="timePeriod"
                    mode="range"
                    @drag="
                      () => {
                        historicalRangeType = 'custom'
                      }
                    "
                    class="date-picker"
                    :class="{ active: historicalRangeType === 'custom' }"
                    color="purple"
                    is-dark
                  />
                </div>
                <div>
                  <v-button
                    @click.native="rangeLastDay()"
                    :hierachyLevel="'secondary'"
                    :text="'1 Day'"
                    :class="{ active: historicalRangeType === '1-day' }"
                  />
                  <v-button
                    @click.native="rangeLast2Days()"
                    :hierachyLevel="'secondary'"
                    :text="'2 Days'"
                    :class="{ active: historicalRangeType === '2-days' }"
                  />
                  <v-button
                    @click.native="rangeLastWeek()"
                    :hierachyLevel="'secondary'"
                    :text="'1 Week'"
                    :class="{ active: historicalRangeType === '1-week' }"
                  />
                  <v-button
                    @click.native="rangeLastMonth()"
                    :hierachyLevel="'secondary'"
                    :text="'1 Month'"
                    :class="{ active: historicalRangeType === '1-month' }"
                  />
                </div>
              </div>
              <template v-if="historicalDataLoaded && historicalData">
                <div
                  v-for="data in historicalData"
                  :key="data.type"
                  class="historical-chart"
                >
                  <h3 class="sub-heading">
                    {{ data.title }}
                  </h3>
                  <chart
                    :chart-data="data"
                    :options="data.options"
                    class="chart"
                  />
                </div>
              </template>
              <template v-else-if="!historicalData">
                <p>No historical data for this time period.</p>
              </template>
              <template v-else-if="!historicalDataLoaded">
                <p>Historical data loading.</p>
              </template>
            </template>
            <template v-else>
              <p class="heading">Sensor has no climate data.</p>
            </template>
          </div>
        </template>
      </main-panel>
    </template>
  </div>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import SidePanel from './../components/SidePanel/SidePanel.vue'
import vButton from './../components/vButton/vButton.vue'
import RecentClimateData from './../components/RecentClimateData/RecentClimateData.vue'
import {
  patchSensor,
  getClimateData,
  deleteSensor,
  deleteClimateData,
  getSensors
} from './../static/api'
import {
  getBatteryStatusFromVoltage,
  formatClimateData,
  convertTemperature
} from './../static/helpers'
import Chart from './../components/Chart/Chart.js'

import {
  sub,
  startOfYesterday,
  endOfToday,
  startOfToday,
  startOfDay,
  endOfDay,
  parseISO
} from 'date-fns'

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 0
  },
  legend: {
    labels: {
      fontFamily: 'Poppins'
    }
  },
  scales: {
    yAxes: [
      {
        ticks: {
          fontFamily: 'Poppins'
        }
      }
    ],
    xAxes: [
      {
        ticks: {
          fontFamily: 'Poppins'
        }
      }
    ]
  },
  elements: {
    line: {
      tension: 0 // disables bezier curves
    }
  }
}
const darkestColour = '#242424'
const typeColours = {
  temperature: {
    light: '#FFCA95',
    dark: '#EFA050'
  },
  humidity: {
    light: '#BCDFF9',
    dark: '#5CB2F2'
  },
  battery: {
    light: '#ffe78e',
    dark: '#ffdb56'
  },
  pressure: {
    light: '#be96f5',
    dark: '#9450ef'
  }
}

function getTypeColors(lowercaseType) {
  if (typeColours[lowercaseType]) {
    return typeColours[lowercaseType]
  } else {
    return {
      light: '#FFE453',
      dark: '#FFE453'
    }
  }
}

export default {
  name: 'dashboard',
  components: {
    MainPanel,
    SidePanel,
    Chart,
    vButton,
    RecentClimateData
  },
  data: function() {
    return {
      errors: [],
      sensors: [],
      activeSensorID: -1,
      activeSensorIndex: -1,
      historicalData: {},
      historicalDataLoaded: false,
      historicalRangeType: '1-day',
      reloadID: null,
      timePeriod: {
        start: startOfToday(),
        end: endOfToday()
      }
    }
  },
  computed: {
    activeSensor: function() {
      if (this.activeSensorIndex !== -1 && this.activeSensorIndex !== -1) {
        return this.sensors[this.activeSensorIndex]
      }
      return {}
    },
    settings: function() {
      return this.$store.state.user.settings
    },
    mobile: function() {
      return this.$store.state.mobile
    }
  },
  watch: {
    mobile: function(newMobile, oldMobile) {
      if (newMobile !== oldMobile) {
        this.loadHistoricalData(this.activeSensorID)
      }
    },
    sensors: function(newSensors) {
      if (newSensors.length && !this.$store.state.mobile) {
        this.makeNextActiveSensor()
      } else if (!newSensors.length && !this.$store.state.mobile) {
        this.activeSensorID = -1
        this.activeSensorIndex = -1
      }
    },
    activeSensorID: function(newID) {
      this.historicalDataLoaded = false
      if (newID !== -1) {
        this.loadHistoricalData(newID)
      }
    },
    timePeriod: function() {
      this.historicalDataLoaded = false
      if (this.activeSensorID !== -1) {
        this.loadHistoricalData(this.activeSensorID)

        // Set time period to start and end of dates if custom date range is used
        if (this.historicalRangeType === 'custom') {
          const periodStart = startOfDay(this.timePeriod.start)
          const periodEnd = endOfDay(this.timePeriod.end)
          if (
            this.timePeriod.start.toString() !== periodStart.toString() ||
            this.timePeriod.end.toString() !== periodEnd.toString()
          ) {
            this.timePeriod = {
              start: periodStart,
              end: periodEnd
            }
          }
        }
      }
    }
  },
  methods: {
    formatClimateData: formatClimateData,
    getBatteryStatusFromVoltage: getBatteryStatusFromVoltage,
    // Sets active sensor ID and index to the first sensor in the sensors array
    makeNextActiveSensor: function() {
      // Checks if the current active sensor exists in the sensors array
      const activeSensorExists = !!this.sensors.filter(
        sensor => sensor.id === this.activeSensorID
      )
      if (this.activeSensorID === -1 || !activeSensorExists) {
        let lowestSensorID = -1
        let lowestIndex = -1

        // Finds the lowest sensor ID in the sensors array
        this.sensors.forEach((sensor, index) => {
          if (lowestSensorID === -1 || sensor.id < lowestSensorID) {
            lowestSensorID = sensor.id
            lowestIndex = index
          }
        })

        // Makes the lowest sensor ID active
        if (lowestSensorID !== -1 && lowestIndex !== -1) {
          this.activeSensorID = lowestSensorID
          this.activeSensorIndex = lowestIndex
        }
      }
    },
    // Updates the sensor's name in the database
    changeSensorName: function(sensorID, sensorName) {
      // Disable name editing for any sensor names being edited
      this.sensors.forEach(sensor => {
        sensor.editing = false
      })

      const accessToken = this.$store.state.user.access_token
      const patchData = {
        name: sensorName
      }
      // Update sensor with new name
      patchSensor(accessToken, sensorID, patchData)
        .then(response => {
          const data = response.data
          if (data.status) {
            this.$toasted.show('Sensor node name changed')
          }
        })
        .catch(e => {
          console.warn(e)
        })
    },
    // Process historical climate data and generate the charts for each type of climate data
    processHistoricalData: function(climateData) {
      // Disable existing charts so that the new charts can be generated
      this.historicalData = []
      this.historicalDataLoaded = false

      const historicalData = {}
      const dates = []
      const orderedClimateData = climateData.slice().reverse()
      const recentClimateData = climateData[0]
      const labels = []

      // Error out if the sensor has no climate data
      if (!recentClimateData || !recentClimateData.climate_data) {
        return false
      }

      // Create battery chart options
      const batteryChartOptions = Object.assign({}, chartOptions)
      batteryChartOptions.scales = {
        yAxes: [
          {
            ticks: {
              beginAtZero: false,
              callback: function(value) {
                return `${value}v`
              },
              source: 'labels',
              fontFamily: 'Poppins',
              fontColor: darkestColour
            }
          }
        ],
        xAxes: [
          {
            type: 'time',
            distribution: 'series',
            time: {
              unit: 'custom',
              displayFormats: {
                custom: 'h:mma D MMM'
              }
            },
            ticks: {
              source: 'labels',
              fontFamily: 'Poppins',
              fontColor: darkestColour,
              display: !this.mobile
            }
          }
        ]
      }

      const batteryColours = getTypeColors('battery')
      // Create battery chart data
      historicalData['battery'] = {
        title: 'Battery Level',
        labels: dates,
        datasets: [
          {
            label: 'Battery Voltage (v)',
            backgroundColor: batteryColours.light,
            borderColor: batteryColours.dark,
            pointBackgroundColor: '#313131',
            pointBorderWidth: 0,
            pointBorderColor: 'transparent',
            pointRadius: 3.5,
            borderWidth: 4,
            spanGaps: true,
            data: [],
            lineTension: 0
          }
        ],
        options: batteryChartOptions
      }

      // Collect sensor types from recent climate data
      for (let climateSensor of recentClimateData.climate_data) {
        const type = climateSensor.type
        let unit = climateSensor.unit
        let value = climateSensor.value

        labels.push(type)
        const lowercaseType = type.toLowerCase()
        const climateChartOptions = Object.assign({}, chartOptions)

        // Format temperature data
        if (type === 'Temperature') {
          unit = `°${this.settings.temperature_unit.toUpperCase()}`
          value = convertTemperature(value, this.settings.temperature_unit)
        }

        // Create chart options
        climateChartOptions.scales = {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
                callback: function(value) {
                  return `${value}${unit}`
                },
                source: 'labels',
                fontFamily: 'Poppins',
                fontColor: darkestColour
              }
            }
          ],
          xAxes: [
            {
              type: 'time',
              distribution: 'series',
              time: {
                unit: 'custom',
                displayFormats: {
                  custom: 'h:mma D MMM'
                }
              },
              ticks: {
                source: 'labels',
                fontFamily: 'Poppins',
                fontColor: darkestColour,
                display: !this.mobile
              }
            }
          ]
        }

        const typeColour = getTypeColors(lowercaseType)
        // Create chart data
        historicalData[lowercaseType] = {
          title: type,
          labels: dates,
          datasets: [
            {
              label: `${type} (${unit})`,
              backgroundColor: typeColour.light,
              borderColor: typeColour.dark,
              spanGaps: true,
              data: [],
              pointBackgroundColor: '#313131',
              pointBorderWidth: 0,
              pointBorderColor: 'transparent',
              pointRadius: 3.5,
              lineTension: 0
            }
          ],
          options: climateChartOptions
        }
      }

      // Put climate data into the corresponding datasets
      orderedClimateData.forEach(climate => {
        dates.push(parseISO(climate.date))
        historicalData['battery'].datasets[0].data.push(climate.battery_voltage)
        if (climate.climate_data) {
          const climate_data = climate.climate_data
          const usedTypes = []

          // Put sensor data into the dataset for each type of climate data
          climate_data.forEach(sensor => {
            let value = sensor.value
            if (sensor.type === 'Temperature') {
              value = convertTemperature(value, this.settings.temperature_unit)
            }
            usedTypes.push(sensor.type)

            if (historicalData[sensor.type.toLowerCase()]) {
              historicalData[sensor.type.toLowerCase()].datasets[0].data.push(
                value
              )
            }
          })

          // Put null data to fill gaps in charts if sensor type is missing from
          // the current climate data object but is in other objects
          labels.forEach(label => {
            if (usedTypes.indexOf(label) === -1) {
              historicalData[label.toLowerCase()].datasets[0].data.push(null)
            }
          })
        }
      })
      this.historicalData = historicalData
      setTimeout(() => {
        this.historicalDataLoaded = true
      }, 10)
    },
    // Retrieve historical climate data for the sensor and generate the historical data charts
    loadHistoricalData: function(sensorID) {
      const accessToken = this.$store.state.user.access_token
      const timePeriod = this.timePeriod
      const rangeStart = timePeriod.start.toISOString()
      const rangeEnd = timePeriod.end.toISOString()

      // Retrieve historical climate data
      getClimateData(accessToken, sensorID, 20, rangeStart, rangeEnd)
        .then(response => {
          const data = response.data
          if (data.climate_data) {
            this.processHistoricalData(data.climate_data)
          }
        })
        .catch(e => {
          console.warn(e)
          this.$toasted.show('Error retrieving historical data')
        })
    },
    // Activates the config actions interface for the specified sensor
    setSensorConfig: function(sensorID) {
      // Finds the sensor that matches the sensorID
      const selectedSensor = this.sensors.filter(sensor => {
        if (sensorID !== sensor.id) {
          sensor.config = false
        }
        return sensor.id === sensorID
      })[0]

      // Toggles visibility of the config actions interface
      if (selectedSensor) {
        selectedSensor.config = !selectedSensor.config
      }
    },
    // Activates the editing actions interface for the specified sensor
    setSensorEditing: function(sensorID) {
      const selectedSensor = this.sensors.filter(sensor => {
        if (sensorID !== sensor.id) {
          sensor.editing = false
        }
        return sensor.id === sensorID
      })[0]
      if (selectedSensor) {
        selectedSensor.editing = !selectedSensor.editing

        // Focus edit input
        const ref = `sensor_name_${selectedSensor.id}`
        const test = this
        this.$nextTick().then(function() {
          test.$refs[ref][0].focus()
        })
      }
    },
    // Makes the specified sensor active so that it's climate data is visible
    setActiveSensor: function(sensorID) {
      // Find the sensor that matches the sensorID
      const activeSensor = this.sensors.filter(
        sensor => sensor.id === sensorID
      )[0]

      // Makes the sensor active
      if (activeSensor) {
        this.activeSensorID = activeSensor.id
        this.activeSensorIndex = this.sensors.indexOf(activeSensor)
      }
    },
    // Deletes the sensor from the database
    deleteSensor: function(sensorID, sensorName) {
      const accessToken = this.$store.state.user.access_token
      deleteSensor(accessToken, sensorID)
        .then(response => {
          const data = response.data
          if (data && data.status) {
            this.$toasted.show(`Deleted sensor node: ${sensorName}`)

            // Locally remove the deleted sensor
            this.sensors = this.sensors.filter(sensor => sensor.id !== sensorID)

            // If the active sensor has been deleted then make the next sensor active
            if (sensorID === this.activeSensorID && !this.$store.state.mobile) {
              this.activeSensorIndex = -1
              this.activeSensorID = -1
              this.makeNextActiveSensor()
            }
          }
        })
        .catch(e => {
          if (e.response) {
            console.warn(e.response)
          }
        })
    },
    // Deletes the sensors climate data from the database
    deleteClimate: function(sensorID, sensorName) {
      const accessToken = this.$store.state.user.access_token
      const sensor = this.sensors.filter(sensor => sensor.id === sensorID)[0]
      if (sensor) {
        sensor.climate_data = []
        sensor.recent_climate_data = null
      }
      deleteClimateData(accessToken, sensorID)
        .then(response => {
          const data = response.data
          if (data && data.status) {
            const sensor = this.sensors.filter(
              sensor => sensor.id === sensorID
            )[0]
            if (sensor) {
              sensor.climate_data = []
              sensor.recent_climate_data = null
              this.$toasted.show(
                `Deleted climate data for sensor node: ${sensorName}`
              )
            }
          }
        })
        .catch(e => {
          if (e.response) {
            console.warn(e.response)
          }
        })
    },
    // Reloads the dashboard with new sensor data
    refreshSensors: function() {
      this.$toasted.show('Refreshing sensor nodes')
      this.loadDashboard()
    },
    // Loads the dashboard's data from the API
    loadDashboard: function() {
      // If a sensor is active then retrieve the historical data
      if (this.activeSensorID !== -1) {
        this.loadHistoricalData(this.activeSensorID)
      }

      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        getSensors(accessToken)
          .then(response => {
            const data = response.data
            if (data.sensors) {
              for (let sensor of data.sensors) {
                sensor.historical_data = []

                // Preserve config and sensor name editing when sensors are reloaded
                const oldSensors = this.sensors.slice()
                if (oldSensors.length) {
                  const oldSensor = this.sensors.filter(
                    oldSensor => oldSensor.id === sensor.id
                  )[0]
                  if (oldSensor) {
                    sensor.config = oldSensor.config
                    sensor.editing = oldSensor.editing
                  } else {
                    sensor.config = false
                    sensor.editing = false
                  }
                } else {
                  sensor.config = false
                  sensor.editing = false
                }
              }
              this.sensors = data.sensors

              if (document.hasFocus()) {
                this.$toasted.show('Loaded climate data')
              }
            }
          })
          .catch(e => {
            if (e.response && e.response.data) {
              this.$router.push('/login')
            }
          })
      } else {
        this.$router.push('/login')
      }
    },
    // Reload dashboard every minute
    createDashboardReloadInterval: function() {
      this.reloadID = setInterval(() => {
        this.loadDashboard(false)
      }, 60000)
    },
    // Initialise the dashboard
    initDashboard: function() {
      // Load the dashboard immediately if logged in or wait
      // to see if user can be logged in from localstorage data
      if (this.$store.state.user.logged_in) {
        this.loadDashboard(true)
        this.createDashboardReloadInterval()
      } else {
        setTimeout(() => {
          this.loadDashboard(true)
          this.createDashboardReloadInterval()
        }, 100)
      }
    },
    // Deactivate the current active sensor
    backToSensorList: function() {
      this.activeSensorID = -1
      this.activeSensorIndex = -1
    },
    // Sets the historical time period to 1 day
    rangeLastDay: function() {
      this.historicalRangeType = '1-day'
      this.timePeriod = {
        start: startOfToday(),
        end: endOfToday()
      }
    },
    // Sets the historical time period to 2 days
    rangeLast2Days: function() {
      this.historicalRangeType = '2-days'
      this.timePeriod = {
        start: startOfYesterday(),
        end: endOfToday()
      }
    },
    // Sets the historical time period to 1 week
    rangeLastWeek: function() {
      this.historicalRangeType = '1-week'
      const date = sub(startOfToday(), { days: 7 })

      this.timePeriod = {
        start: date,
        end: endOfToday()
      }
    },
    // Sets the historical time period to 1 month
    rangeLastMonth: function() {
      this.historicalRangeType = '1-month'
      const date = sub(startOfToday(), { months: 1 })

      this.timePeriod = {
        start: date,
        end: endOfToday()
      }
    }
  },
  created: function() {
    this.initDashboard()
  },
  beforeDestroy: function() {
    // Clear dashboard reloading ID before route changes
    if (this.reloadID) {
      clearInterval(this.reloadID)
    }
  }
}
</script>
