<template>
  <main-panel>
    <template slot="content">
      <div class="content-column">
        <h1 class="title">Climate Monitor</h1>
        <h2 class="heading">Reset Password</h2>
        <p class="text">
          Enter a reset token and new password to reset the account password.
        </p>
        <reset-password-form
          :current-reset-token="$store.state.user.reset_token"
        />
      </div>
    </template>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import ResetPasswordForm from './../components/ResetPasswordForm/ResetPasswordForm.vue'

export default {
  name: 'resetpassword',
  components: {
    MainPanel,
    ResetPasswordForm
  }
}
</script>
