<template>
  <div class="content">
    <side-panel
      v-if="
        !$store.state.mobile ||
          ($store.state.mobile && activeSensorIndex === -1)
      "
    >
      <template slot="header">
        <p class="sub-heading">Sensors</p>
        <v-button
          @click.native="refreshSensors"
          :type="'secondary'"
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
              <div style="display: flex; flex-direction: row;">
                <p
                  class="heading"
                  style="margin-right: 0.25em; display: flex; align-items: center;"
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
                  style="margin-right: 0.25em; display: flex; align-items: center;"
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
                  v-if="sensor.editing"
                />
                <v-button
                  @click.native="setSensorEditing(sensor.id)"
                  :type="'tertiary'"
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
                    <template
                      v-if="
                        data.type === 'Temperature' || data.type === 'Humidity'
                      "
                    >
                      <p class="text text--bold" style="margin: 0.5em 0 0 0;">
                        {{ data.type }}: {{ data.value }}{{ data.unit }}
                      </p>
                    </template>
                  </li>
                </ul>
                <p class="text">
                  Date received: {{ sensor.recent_climate_data.date }}
                </p>
                <p class="text">
                  Battery level:
                  {{
                    getBatteryStatusFromVoltage(
                      sensor.recent_climate_data.battery_voltage
                    )
                  }}
                </p>
              </div>
              <div v-else>
                <p class="text">No climate data for this sensor</p>
              </div>
              <div class="actions">
                <v-button
                  @click.native="setSensorConfig(sensor.id)"
                  :type="'secondary'"
                  :text="sensor.config ? 'close' : 'settings'"
                  :isIcon="true"
                />
                <v-button
                  @click.native="setActiveSensor(sensor.id)"
                  :type="'primary'"
                  :text="'View Climate'"
                />
              </div>
              <div
                v-if="sensor.config"
                :class="['actions', { 'actions--active': sensor.config }]"
              >
                <v-button
                  @click.native="deleteSensor(sensor.id, sensor.name)"
                  :type="'tertiary'"
                  :text="'Delete Sensor'"
                />
                <v-button
                  @click.native="deleteClimate(sensor.id, sensor.name)"
                  :type="'tertiary'"
                  :text="'Delete Climate Data'"
                />
              </div>
            </template>
          </li>
        </ul>
        <ul v-else class="list">
          <li class="list-item">
            <p class="text">
              No sensors created. Connect a sensor node to the base station to
              create a new sensor.
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
      <main-panel v-else-if="sensors[activeSensorIndex]">
        <template slot="header">
          <p class="sub-heading">
            Node {{ sensors[activeSensorIndex].id }}:
            {{ sensors[activeSensorIndex].name }}
          </p>
          <v-button
            @click.native="refreshSensors"
            :type="'secondary'"
            :text="'refresh'"
            :isIcon="true"
          />
        </template>
        <template slot="content">
          <div class="dashboard-content">
            <v-button
              v-if="$store.state.mobile"
              @click.native="backToSensorList()"
              :type="'tertiary'"
              :text="'Back'"
            />
            <template
              v-if="
                sensors[activeSensorIndex] &&
                  sensors[activeSensorIndex].recent_climate_data
              "
            >
              <h3 class="heading">Recent Climate Data</h3>
              <p class="text">
                Date received:
                {{ sensors[activeSensorIndex].recent_climate_data.date }}
              </p>
              <ul class="recent-data-list">
                <li
                  v-for="(data, index) in sensors[activeSensorIndex]
                    .recent_climate_data.climate_data"
                  :key="index"
                >
                  <p class="text">{{ data.type }}</p>
                  <p class="sub-heading">{{ data.value }}{{ data.unit }}</p>
                </li>
              </ul>

              <h3 class="heading">Historical Climate Data</h3>
              <div class="input-box">
                <p class="text">Historical Range</p>
                <v-date-picker v-model="timePeriod" mode="range" />
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
              <template v-else>
                <p>No historical data for this time period.</p>
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
import { HTTP } from './../static/http-common'
import { getBatteryStatusFromVoltage } from './../static/helpers'
import Chart from './../components/Chart/Chart.js'

export default {
  name: 'dashboard',
  components: {
    MainPanel,
    SidePanel,
    Chart,
    vButton
  },
  data: function() {
    return {
      errors: [],
      sensors: [],
      activeSensorID: -1,
      activeSensorIndex: -1,
      historicalData: {},
      historicalDataLoaded: false,
      reloadID: null,
      timePeriod: {
        start: new Date(Date.now() - 86400000),
        end: new Date()
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          labels: {
            fontFamily: 'Poppins'
          }
        },
        scales: {
          yAxes: [
            {
              ticks: {
                fontFamily: 'Arial'
              }
            }
          ],
          xAxes: [
            {
              ticks: {
                fontFamily: 'Arial'
              }
            }
          ]
        }
      }
    }
  },
  watch: {
    sensors: function(newSensors) {
      if (newSensors.length && !this.$store.state.mobile) {
        const activeSensorExists = !!this.sensors.filter(
          sensor => sensor.id === this.activeSensorID
        )
        if (this.activeSensorID === -1 || !activeSensorExists) {
          let lowestSensorID = -1
          let lowestIndex = -1
          this.sensors.forEach((sensor, index) => {
            if (lowestSensorID === -1 || sensor.id < lowestSensorID) {
              lowestSensorID = sensor.id
              lowestIndex = index
            }
          })
          if (lowestSensorID !== -1 && lowestIndex !== -1) {
            this.activeSensorID = lowestSensorID
            this.activeSensorIndex = lowestIndex
          }
        }
      } else {
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
      }
    }
  },
  methods: {
    getBatteryStatusFromVoltage: getBatteryStatusFromVoltage,
    changeSensorName: function(sensorID, sensorName) {
      const accessToken = this.$store.state.user.access_token

      HTTP.patch(
        `sensors/${sensorID}`,
        {
          name: sensorName
        },
        { headers: { Authorization: 'Bearer ' + accessToken } }
      )
        .then(response => {
          console.log(response)
          const data = response.data
          if (data.status) {
            this.$toasted.show('Sensor name changed')
          }
        })
        .catch(e => {
          console.log(e)
        })
    },
    processHistoricalData: function(climateData) {
      this.historicalData = []
      this.historicalData = false
      const historicalData = {}
      const dates = []
      const typeColours = {
        temperature: '#f87979',
        humidity: '#79a6f8',
        battery: '#FFE453'
      }

      const orderedClimateData = climateData.reverse()
      const recentClimateData = orderedClimateData[0]
      const labels = []
      if (!recentClimateData || !recentClimateData.climate_data) {
        return false
      }

      const batteryChartOptions = Object.assign({}, this.chartOptions)
      batteryChartOptions.scales = {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return `${value}v`
              }
            }
          }
        ]
      }

      historicalData['battery'] = {
        title: 'Battery Level',
        labels: dates,
        datasets: [
          {
            label: 'Battery Voltage (v)',
            backgroundColor: typeColours['battery'],
            data: []
          }
        ],
        options: batteryChartOptions
      }

      // Collect sensor types from recent climate data
      for (let climateSensor of recentClimateData.climate_data) {
        const type = climateSensor.type
        const unit = climateSensor.unit
        labels.push(type)
        const lowercaseType = type.toLowerCase()
        const chartOptions = Object.assign({}, this.chartOptions)
        chartOptions.scales = {
          yAxes: [
            {
              ticks: {
                beginAtZero: true,
                callback: function(value) {
                  return `${value}${unit}`
                }
              }
            }
          ]
        }

        historicalData[lowercaseType] = {
          title: type,
          labels: dates,
          datasets: [
            {
              label: `${type} (${unit})`,
              backgroundColor: typeColours[lowercaseType],
              data: []
            }
          ],
          options: chartOptions
        }
      }

      // Put climate data into the corresponding datasets
      orderedClimateData.forEach(climate => {
        dates.push(climate.date)
        historicalData['battery'].datasets[0].data.push(climate.battery_voltage)
        if (climate.climate_data) {
          const climate_data = climate.climate_data
          climate_data.forEach(sensor => {
            historicalData[sensor.type.toLowerCase()].datasets[0].data.push(
              sensor.value
            )
          })
        }
      })
      this.historicalData = historicalData
      this.historicalDataLoaded = true
    },
    loadHistoricalData: function(sensorID) {
      console.log('Loading historical')
      const accessToken = this.$store.state.user.access_token
      const timePeriod = this.timePeriod
      const rangeStart = timePeriod.start.toISOString()
      const rangeEnd = timePeriod.end.toISOString()

      HTTP.get(
        `sensors/${sensorID}/climate-data?range_start=${rangeStart}&range_end=${rangeEnd}`,
        {
          headers: { Authorization: 'Bearer ' + accessToken }
        }
      )
        .then(response => {
          console.log(response)
          const data = response.data
          if (data.climate_data) {
            this.processHistoricalData(data.climate_data)
          }
        })
        .catch(e => {
          console.log(e)
          this.$toasted.show('Error retrieving historical data')
        })
    },
    setSensorConfig: function(sensorID) {
      const selectedSensor = this.sensors.filter(sensor => {
        if (sensorID !== sensor.id) {
          sensor.config = false
        }
        return sensor.id === sensorID
      })[0]
      if (selectedSensor) {
        selectedSensor.config = !selectedSensor.config
      }
    },
    setSensorEditing: function(sensorID) {
      const selectedSensor = this.sensors.filter(
        sensor => sensor.id === sensorID
      )[0]
      if (selectedSensor) {
        selectedSensor.editing = !selectedSensor.editing
      }
    },
    setActiveSensor: function(sensorID) {
      const activeSensor = this.sensors.filter(
        sensor => sensor.id === sensorID
      )[0]
      if (activeSensor) {
        this.activeSensorID = activeSensor.id
        this.activeSensorIndex = this.sensors.indexOf(activeSensor)
      }
    },
    deleteSensor: function(sensorID, sensorName) {
      const accessToken = this.$store.state.user.access_token
      HTTP.delete(`sensors/${sensorID}`, {
        headers: { Authorization: 'Bearer ' + accessToken }
      })
        .then(response => {
          const data = response.data
          if (data && data.status) {
            this.$toasted.show(`Deleted sensor ${sensorName}`)
            this.sensors = this.sensors.filter(sensor => sensor.id !== sensorID)
          }
        })
        .catch(e => {
          if (e.response) {
            console.log(e.response)
          }
        })
    },
    deleteClimate: function(sensorID, sensorName) {
      const accessToken = this.$store.state.user.access_token
      HTTP.delete(`sensors/${sensorID}/climate-data`, {
        headers: { Authorization: 'Bearer ' + accessToken }
      })
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
                `Deleted climate data for sensor: ${sensorName}`
              )
            }
          }
        })
        .catch(e => {
          if (e.response) {
            console.log(e.response)
          }
        })
    },
    refreshSensors: function() {
      this.$toasted.show('Refreshing sensors')
      this.loadDashboard()
    },
    loadDashboard: function() {
      if (this.activeSensorID !== -1) {
        this.loadHistoricalData(this.activeSensorID)
      }

      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        HTTP.get('sensors', {
          headers: { Authorization: 'Bearer ' + accessToken }
        })
          .then(response => {
            console.log(response)
            const data = response.data
            if (data.sensors) {
              for (let sensor of data.sensors) {
                sensor.historical_data = []
                sensor.config = false
                sensor.editing = false
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
    createDashboardReloadInterval: function() {
      // Reload dashboard every minute
      this.reloadID = setInterval(() => {
        this.loadDashboard(false)
      }, 60000)
    },
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
        }, 150)
      }
    },
    backToSensorList: function() {
      this.activeSensorID = -1
      this.activeSensorIndex = -1
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
