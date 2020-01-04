<template>
  <div class="home">
    <p>Login</p>
    <div>
      <input type="text" v-model="email" placeholder="Email">
      <input type="text" v-model="password" placeholder="Password">
      <button @click="login">Login</button>
    </div>
    <div>
      <ul>
        <li v-for="(error, index) in errors" :key="index">
          <p>{{error}}</p>
        </li>
      </ul>
    </div>
    <router-link to="/reset-password">Reset Password</router-link>
  </div>
</template>

<script>
import {HTTP} from './../static/http-common';

export default {
  name: "login",
  data: function() {
    return {
      email: '',
      password: '',
      errors: []
    }
  },
  methods: {
    login: function() {
      this.errors = []
      const email = this.email
      const password = this.password

      HTTP.post(`/login`, {
        email: email,
        password: password
      })
      .then(response => {
        console.log(response)
        const data = response.data
        if (data.status && data.access_token && data.refresh_token) {
          const user = this.$store.state.user
          user.logged_in = true
          user.access_token = data.access_token
          user.refresh_token = data.refresh_token
          user.email = email
          user.user_id = 1
          this.$store.commit('setUser', user)
          console.log('Logged in')
        }

      })
      .catch(e => {
        if (e.response && e.response.data) {
          const errors = e.response.data.errors
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
