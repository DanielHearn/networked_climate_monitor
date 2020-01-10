<template>
  <div class="content">
    <side-panel>
      <template slot="header">
        <p class="text">Sensors</p>
        <button @click="refreshSensors">Refresh Sensors</button>
      </template>
      <template slot="content">
        <ul>
          <li v-for="sensor in sensors" :key="sensor.id">
            <p class="text">{{sensor.id}}: {{sensor.name}}</p>
            <div v-if="sensor.recent_climate_data">
              <ul>
                <li v-for="(data, index) in sensor.recent_climate_data.climate_data" :key="index">
                  <template v-if="data.type === 'Temperature' || data.type === 'Humidity'">  
                    <p class="text">{{data.type}}: {{data.value}}{{data.unit}}</p>
                  </template>
                </li>
              </ul>
              <p class="text">Date received: {{sensor.recent_climate_data.date}}</p>
              <p class="text">Battery voltage: {{getBatteryStatusFromVoltage(sensor.recent_climate_data.battery_voltage)}}</p>
            </div>
            <div v-else>
              <p class="text">No climate data for sensor</p>
            </div>
            <button @click="deleteSensor(sensor.id, sensor.name)">Delete Sensor</button>
            <button @click="deleteClimate(sensor.id, sensor.name)">Delete Climate Data</button>
            <button @click="setActiveSensor(sensor.id)">View Climate</button>
          </li>
        </ul>
      </template>
    </side-panel>
    <main-panel v-if="activeSensorID === -1"> 
      <template slot="header">
        <p class="text">Climate Data</p>
      </template>
      <template slot="content">
        <p class="text">No sensor selected</p>
      </template>
    </main-panel>
    <main-panel v-else>
      <template slot="header">
        <p class="text">{{sensors[activeSensorID].name}} Climate Data</p>
        <button >Refresh ClimateData</button>
      </template>
      <template slot="content">
        <div v-if="sensors[activeSensorID]">
          <div v-if="sensors[activeSensorID].recent_climate_data">
            <h3 class="heading">Recent Sensor Data</h3>
            <p class="text">Date received: {{sensors[activeSensorID].recent_climate_data.date}}</p>
            <ul>
              <li v-for="(data, index) in sensors[activeSensorID].recent_climate_data.climate_data" :key="index">
                <p>{{data.type}}: {{data.value}}{{data.unit}}</p>
              </li>
            </ul>

            <h3 class="heading">Historical Sensor Data</h3>
              <v-date-picker
              v-model="timePeriod"
              mode="range"
              />
          </div>
          <div v-else>
            <p class="text">Sensor has no climate data.</p>
          </div>
        </div>
      </template>
    </main-panel>
  </div>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import SidePanel from './../components/SidePanel/SidePanel.vue'
import {HTTP} from './../static/http-common';
import {getBatteryStatusFromVoltage} from './../static/helpers'
//import Chart from './../components/Chart/Chart.js'

export default {
  name: "dashboard",
  components: {
    MainPanel,
    SidePanel
    //Chart
  },
  data: function() {
    return {
      errors: [],
      sensors: [],
      activeSensorID: -1,
      timePeriod: {
        start: Date.now(),
        end: Date.now()
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
          this.activeSensorID = lowestIndex
        }

      }
    }
  },
  methods: {
    getBatteryStatusFromVoltage: getBatteryStatusFromVoltage,
    setActiveSensor: function(sensorID) {
      const activeSensor = this.sensors.filter(sensor => sensor.id === sensorID)[0]
      this.activeSensorID = this.sensors.indexOf(activeSensor)
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
    loadDashboard: function() {
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
      this.loadDashboard()
    } else{
      setTimeout(() => {
        this.loadDashboard()
      }, 150)
    }
  }
};
</script>
