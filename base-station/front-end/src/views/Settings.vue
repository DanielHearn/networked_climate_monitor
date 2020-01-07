<template>
  <div class="home">
    <p>Settings</p>
    <div>
      <p v-if="!$store.state.user.logged_in">Please log in</p>
      <ul>
        <li v-for="(setting, key) in this.$store.state.user.settings" :key="key">
          <p>{{key}}: {{setting}}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import {HTTP} from './../static/http-common';

export default {
  name: "settings",
  methods: {
    loadSettings: function() {
      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        HTTP.get(`account`, {
          headers: {'Authorization': 'Bearer ' + accessToken},
        })
        .then(response => {
          const data = response.data
          if (data.status && data.account) {
            const user = this.$store.state.user
            user.settings = JSON.parse(data.account.settings.replace(/'/g, '"'))

            this.$store.commit('setUser', user)
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
    console.log('Load settings')

    if (this.$store.state.user.logged_in) {
      this.loadSettings()
    } else{
      setTimeout(() => {
        this.loadSettings()
      }, 150)
    }
  }
};
</script>
