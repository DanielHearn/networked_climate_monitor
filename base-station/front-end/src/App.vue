<template>
  <div id="app">
    <div id="nav">
      <div class="nav__side">
        <p>Climate Monitor</p>
      </div>
      <div class="nav__links">
        <router-link to="/">Home</router-link>
        <router-link to="/login">Login</router-link>
        <router-link to="/register">Register</router-link>
        <router-link to="/dashboard">Dashboard</router-link>
        <router-link to="/settings">Settings</router-link>
      </div>
      <div class="nav__side">
        <button v-if="$store.state.user.logged_in" @click="logout">Logout</button>
      </div>
    </div>
    <router-view />
  </div>
</template>

<style lang="scss">
@import './app.scss';
</style>

<script>
export default {
  name: "app",
  methods: {
    logout: function() {
      const user = this.$store.state.user
      user.logged_in = false
      user.access_token = ''
      user.refresh_token = ''
      user.email = ''
      user.user_id = 0
      this.$store.commit('setUser', user)

      console.log('Logout')
      this.$toasted.show('Logged out')
      this.$router.push('login')
    }
  }
};
</script>
