<template>
  <main-panel>
    <template slot="content">
      <div class="content-column">
        <h1 class="title">Climate Monitor</h1>
        <h2 class="heading">Login</h2>
        <p class="text">Enter an email and password to login.</p>
        <login-form />
      </div>
    </template>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import LoginForm from './../components/LoginForm/LoginForm.vue'

export default {
  name: 'login',
  components: {
    MainPanel,
    LoginForm
  }
}
</script>
