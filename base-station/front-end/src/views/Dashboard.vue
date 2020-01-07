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
  methods: {
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
