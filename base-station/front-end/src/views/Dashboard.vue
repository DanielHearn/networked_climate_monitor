<template>
  <div class="home">
    <p>Dashboard</p>
    <div>
      <p v-if="!$store.state.user.logged_in">Please log in</p>
      <ul>
        <li v-for="sensor in sensors" :key="sensor.id">
          <p>{{sensor.name}}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import {HTTP} from './../static/http-common';

export default {
  name: "dashboard",
  data: function() {
    return {
      errors: [],
      sensors: []
    }
  },
  created: function() {
    console.log('Load dashboard')

    if (this.$store.state.user.logged_in) {
      HTTP.get(`/sensors`, {
        headers: {'Authorization': 'Bearer ' + this.$store.state.user.access_token},
      })
      .then(response => {
        console.log(response)
        const data = response.data
        if (data.sensors) {
          this.sensors = data.sensors
        }
      })
      .catch(e => {
        if (e.response && e.response.data) {
          const errors = e.response.data
          for (let errorField in errors) {
            const field = errorField
            const fieldErrors = errors[errorField]
            for (let error of fieldErrors) {
              const errorText = `${field}: ${error}`
              this.errors.push(errorText)
            }
          }
        }
      })
    }
  }
};
</script>
