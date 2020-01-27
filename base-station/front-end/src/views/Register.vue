<template>
  <main-panel>
    <template slot="content">
      <div class="content-column">
        <h1 class="title">Climate Monitor</h1>
        <h2 class="heading">Account Registration</h2>
        <p class="text">
          Enter an email and password to register the account.
        </p>
        <register-form />
        <router-link to="/login" class="link"
          >Already registered? Click here to login</router-link
        >
      </div>
    </template>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import RegisterForm from './../components/RegisterForm/RegisterForm.vue'

export default {
  name: 'register',
  components: {
    MainPanel,
    RegisterForm
  }
}
</script>
