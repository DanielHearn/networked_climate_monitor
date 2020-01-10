<template>
  <div class="content">
    <side-panel>
      <template slot="header">
        <p class="heading">Sensors</p>
        <button @click="refreshSensors" class="button button--primary">Refresh Sensors</button>
      </template>
      <template slot="content">
        <ul class="list">
          <li v-for="sensor in sensors" :key="sensor.id" class="list-item" v-bind:class="{ active: sensor.id === activeSensorID }">
            <p class="heading">{{sensor.id}}: {{sensor.name}}</p>
            <div v-if="sensor.recent_climate_data">
              <ul>
                <li v-for="(data, index) in sensor.recent_climate_data.climate_data" :key="index">
                  <template v-if="data.type === 'Temperature' || data.type === 'Humidity'">  
                    <p class="sub-heading">{{data.type}}: {{data.value}}{{data.unit}}</p>
                  </template>
                </li>
              </ul>
              <p class="text">Date received: {{sensor.recent_climate_data.date}}</p>
              <p class="text">Battery voltage: {{getBatteryStatusFromVoltage(sensor.recent_climate_data.battery_voltage)}}</p>
            </div>
            <div v-else>
              <p class="text">No climate data for sensor</p>
            </div>
            <div>
              <button @click="setActiveSensor(sensor.id)" class="button button--primary">View Climate</button>
            </div>
            <div>
              <button @click="deleteSensor(sensor.id, sensor.name)" class="button button--secondary">Delete Sensor</button>
              <button @click="deleteClimate(sensor.id, sensor.name)" class="button button--secondary">Delete Climate Data</button>
            </div>
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
          <p class="heading">{{sensors[activeSensorIndex].name}} Climate Data</p>
          <button @click="refreshSensors" class="button button--primary">Refresh Climate Data</button>
        </template>
        <template slot="content">
          <div class="dashboard-content">
            <template v-if="sensors[activeSensorIndex] && sensors[activeSensorIndex].recent_climate_data">
              <h3 class="sub-heading">Recent Sensor Data</h3>
              <p class="text">Date received: {{sensors[activeSensorIndex].recent_climate_data.date}}</p>
              <ul class="recent-data-list">
                <li v-for="(data, index) in sensors[activeSensorIndex].recent_climate_data.climate_data" :key="index">
                  <p class="text">{{data.type}}</p>
                  <p class="sub-heading">{{data.value}}{{data.unit}}</p>
                </li>
              </ul>

              <h3 class="sub-heading">Historical Sensor Data</h3>
              <v-date-picker
              v-model="timePeriod"
              mode="range"
              />
              <template v-if="historicalDataLoaded && historicalData">
                  <chart v-for="data in historicalData" :key="data.type" :chart-data="data" :options="chartOptions" class="historical-chart"/>
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
import {HTTP} from './../static/http-common';
import {getBatteryStatusFromVoltage} from './../static/helpers'
import Chart from './../components/Chart/Chart.js'

export default {
  name: "dashboard",
  components: {
    MainPanel,
    SidePanel,
    Chart
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
        start: new Date(Date.now()-86400000),
        end: new Date()
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false
      }
    }
  },
  watch: {
    sensors: function (newSensors) {
      if (newSensors.length && this.activeSensorID === -1) {
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
    },
    activeSensorID: function(newID) {
      this.historicalDataLoaded = false
      this.loadHistoricalData(newID)
    },
    timePeriod: function() {
      this.historicalDataLoaded = false
      this.loadHistoricalData(this.activeSensorID)
    }
  },
  methods: {
    getBatteryStatusFromVoltage: getBatteryStatusFromVoltage,
    processHistoricalData: function(climateData) {
      const historicalData = {}
      const dates = []
      const typeColours = {
        'temperature': '#f87979',
        'humidity': '#79a6f8',
        'battery': '#FFE453'
      }
      
      const orderedClimateData = climateData.reverse()
      const recentClimateData = orderedClimateData[0]
      const labels = []
      if (!recentClimateData || !recentClimateData.climate_data) {
        return false
      }

      historicalData['battery'] = {
        labels: dates,
        datasets: [{
          label: 'Battery',
          backgroundColor: typeColours['battery'],
          data: []
        }]
      }

      for (let climateSensor of recentClimateData.climate_data) {
        const type = climateSensor.type
        labels.push(type)
        const lowercaseType = type.toLowerCase()

        historicalData[lowercaseType] = {
          labels: dates,
          datasets: [{
            label: type,
            backgroundColor: typeColours[lowercaseType],
            data: []
          }]
        }
      }

      orderedClimateData.forEach(climate => {
        dates.push(climate.date)
        historicalData['battery'].datasets[0].data.push(climate.battery_voltage)
        if (climate.climate_data) {
          const climate_data = climate.climate_data
          climate_data.forEach(sensor => {
            historicalData[sensor.type.toLowerCase()].datasets[0].data.push(sensor.value)
          });
        }
      });
      console.log(historicalData)
      this.historicalData = historicalData
      this.historicalDataLoaded = true
    },
    loadHistoricalData: function(sensorID) {
      const accessToken = this.$store.state.user.access_token
      const timePeriod = this.timePeriod
      const rangeStart = timePeriod.start.toISOString()
      const rangeEnd = timePeriod.end.toISOString()

      HTTP.get(`sensors/${sensorID}/climate-data?range_start=${rangeStart}&range_end=${rangeEnd}`, {
        headers: {'Authorization': 'Bearer ' + accessToken},
      })
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
    setActiveSensor: function(sensorID) {
      const activeSensor = this.sensors.filter(sensor => sensor.id === sensorID)[0]
      this.activeSensorID = activeSensor.id
      this.activeSensorIndex = this.sensors.indexOf(activeSensor)
    },
    deleteSensor: function(sensorID, sensorName) {
      const accessToken = this.$store.state.user.access_token
      HTTP.delete(`sensors/${sensorID}`, {
        headers: {'Authorization': 'Bearer ' + accessToken}
      })
      .then(response => {
        const data = response.data
        if (data && data.status) {
          this.$toasted.show(`Deleted sensor ${sensorName}`)
          const sensors = this.sensors.slice()
          this.sensors = sensors.filter(sensor => sensor.id !== sensorID)
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
        headers: {'Authorization': 'Bearer ' + accessToken}
      })
      .then(response => {
        const data = response.data
        if (data && data.status) {
          this.$toasted.show(`Deleted climate data for sensor: ${sensorName}`)
          const sensor = this.sensors.filter(sensor => sensor.id === sensorID)[0]
          if (sensor) {
            sensor.climate_data = []
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
    loadDashboard: function(firstLoad = false) {
      if (firstLoad) {
        if(this.reloadID) {
          clearInterval(this.reloadID)
        }
        this.reloadID = setInterval(() => {
          this.loadDashboard(false)
        }, 60000)
      }

      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        HTTP.get(`sensors`, {
          headers: {'Authorization': 'Bearer ' + accessToken},
        })
        .then(response => {
          console.log(response)
          const data = response.data
          if (data.sensors) {
            for (let sensor of data.sensors) {
              sensor.historical_data = []
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
    }
  },
  created: function() {
    console.log('Load dashboard')

    if (this.$store.state.user.logged_in) {
      this.loadDashboard(true)
    } else{
      setTimeout(() => {
        this.loadDashboard(true)
      }, 150)
    }
  }
};
</script>
