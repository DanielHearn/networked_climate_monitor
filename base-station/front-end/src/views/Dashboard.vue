<template>
  <div class="content">
    <side-panel>
      <template slot="header">
        <p class="heading">Sensors</p>
        <v-button
          @click.native="refreshSensors"
          :type="'primary'"
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
                <p class="heading">{{ sensor.id }}:</p>
                <input
                  type="text"
                  v-model="sensor.name"
                  v-on:change="changeSensorName(sensor.id, sensor.name)"
                />
              </div>
              <div v-if="sensor.recent_climate_data">
                <ul
                  style="list-style: none; padding: 0; display: flex; flex-direction: row;"
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
                      <p class="sub-heading">
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
                <p class="text">No climate data for sensor</p>
              </div>
              <div class="actions">
                <v-button
                  @click.native="setSensorConfig(sensor.id)"
                  :type="'secondary'"
                  :text="'settings'"
                  :isIcon="true"
                />
                <button
                  @click="setActiveSensor(sensor.id)"
                  class="button button--primary"
                >
                  View Climate
                </button>
              </div>
              <div
                v-if="sensor.config"
                :class="['actions', { 'actions--active': sensor.config }]"
              >
                <button
                  @click="deleteSensor(sensor.id, sensor.name)"
                  class="button button--secondary"
                >
                  Delete Sensor
                </button>
                <button
                  @click="deleteClimate(sensor.id, sensor.name)"
                  class="button button--secondary"
                >
                  Delete Climate Data
                </button>
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
    <template v-if="!$store.state.mobile">
      <main-panel v-if="activeSensorIndex === -1">
        <template slot="header">
          <p class="heading">Climate Data</p>
        </template>
        <template slot="content">
          <p class="text">No sensor selected</p>
        </template>
      </main-panel>
      <main-panel v-else>
        <template slot="header">
          <p class="heading">
            {{ sensors[activeSensorIndex].id }}:
            {{ sensors[activeSensorIndex].name }} Climate Data
          </p>
          <v-button
            @click.native="refreshSensors"
            :type="'primary'"
            :text="'refresh'"
            :isIcon="true"
          />
        </template>
        <template slot="content">
          <div class="dashboard-content">
            <template
              v-if="
                sensors[activeSensorIndex] &&
                  sensors[activeSensorIndex].recent_climate_data
              "
            >
              <h3 class="sub-heading">Recent Sensor Data</h3>
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

              <h3 class="sub-heading">Historical Sensor Data</h3>
              <v-date-picker v-model="timePeriod" mode="range" />
              <template v-if="historicalDataLoaded && historicalData">
                <chart
                  v-for="data in historicalData"
                  :key="data.type"
                  :chart-data="data"
                  :options="chartOptions"
                  class="historical-chart"
                />
              </template>
              <template v-else>
                <p>No historical data for this time period.</p>
              </template>
            </template>
            <template v-else>
              <p class="text">Sensor has no climate data.</p>
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
        maintainAspectRatio: false
      }
    }
  },
  watch: {
    sensors: function(newSensors) {
      if (newSensors.length) {
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

      historicalData['battery'] = {
        labels: dates,
        datasets: [
          {
            label: 'Battery Voltage',
            backgroundColor: typeColours['battery'],
            data: []
          }
        ]
      }

      for (let climateSensor of recentClimateData.climate_data) {
        const type = climateSensor.type
        labels.push(type)
        const lowercaseType = type.toLowerCase()

        historicalData[lowercaseType] = {
          labels: dates,
          datasets: [
            {
              label: type,
              backgroundColor: typeColours[lowercaseType],
              data: []
            }
          ]
        }
      }

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
      const selectedSensor = this.sensors.filter(
        sensor => sensor.id === sensorID
      )[0]
      if (selectedSensor) {
        selectedSensor.config = !selectedSensor.config
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
