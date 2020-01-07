<template>
  <div class="home">
    <p>Dashboard</p>
    <button @click="refreshSensors">Refresh Sensors</button>
    <div>
      <p v-if="!$store.state.user.logged_in">Please log in</p>
      <ul>
        <li v-for="sensor in sensors" :key="sensor.id">
          <p>{{sensor.name}}</p>
          <div v-if="sensor.climate_data && sensor.climate_data.length">
            <p>Date received: {{sensor.climate_data[0].date}}</p>
            <p>Battery voltage: {{getBatteryStatusFromVoltage(sensor.climate_data[0].battery_voltage)}}</p>
            <ul>
              <li v-for="(data, index) in sensor.climate_data[0].climate_data" :key="index">
                <p>{{data.type}}: {{data.value}}{{data.unit}}</p>
              </li>
            </ul>
          </div>
          <div v-else>
            <p>No climate data for sensor</p>
          </div>
          <button @click="deleteSensor(sensor.id, sensor.name)">Delete Sensor</button>
          <button @click="deleteClimate(sensor.id, sensor.name)">Delete Climate Data</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import {HTTP} from './../static/http-common';
import {getBatteryStatusFromVoltage} from './../static/helpers'

export default {
  name: "dashboard",
  data: function() {
    return {
      errors: [],
      sensors: []
    }
  },
  watch: {
    sensors: function (newSensors, oldSensors) {
      if (newSensors !== oldSensors) {
        this.loadRecentClimateData()
      }
    }
  },
  methods: {
    getBatteryStatusFromVoltage: getBatteryStatusFromVoltage,
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
    loadRecentClimateData: function() {
      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        const quantity = 1
        for (let sensor of this.sensors) {
          if (sensor.id) {
            HTTP.get(`sensors/${sensor.id}/climate-data`, {
              headers: {'Authorization': 'Bearer ' + accessToken},
              query: {'quantity': quantity} 
            })
            .then(response => {
              console.log(response)
              const data = response.data
              if (data && data.climate_data) {
                sensor.climate_data = data.climate_data
              }
            })
            .catch(e => {
              if (e.response) {
                console.log(e.respose)
              }
            })
          }
        }
      }
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
              sensor.climate_data = []
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
