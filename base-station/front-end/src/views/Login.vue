<template>
  <div class="home">
    <p>Login</p>
    <div>
      <form
        id="login"
        @submit="checkLogin"
        method="post"
      >
        <input type="text" name="email" v-model="email" placeholder="Email">
        <input type="text" name="password" v-model="password" placeholder="Password">
        <button type="submit" value="Submit">Login</button>
      </form>
    </div>
    <div>
      <ul v-if="errors.length">
        <p>Errors:</p>
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
import {processErrors} from './../static/helpers';

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
    checkLogin: function(e) {
      e.preventDefault();
      this.errors = []

      const email = this.email
      const password = this.password
      let valid = true

      if (email === '') {
        this.errors.push('Enter a email.');
        valid = false
      } else if (email.indexOf('@') === -1) {
        this.errors.push('Enter a valid email.');
        valid = false
      }
      if (password === '') {
        this.errors.push('Enter a password.');
        valid = false
      } else if (password.length < 8 || password.length > 40) {
        this.errors.push('Password must be between 8 and 40 characters long.');
        valid = false
      }

      if (valid) {
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
            this.$toasted.show('Logged in')
          }

        })
        .catch(e => {
          if (e.response && e.response.data && e.response.data.errors) {
            this.errors = processErrors(e.response.data.errors)
          }
        })
      }
    }
  }
};
</script>
