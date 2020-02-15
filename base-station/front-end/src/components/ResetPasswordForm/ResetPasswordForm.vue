<template>
  <form
    id="reset-password-form"
    class="form"
    @submit="checkResetPassword"
    method="post"
  >
    <div class="input-box">
      <p class="text">Reset Token</p>
      <input
        type="text"
        class="input--text"
        name="resetToken"
        v-model="resetToken"
        placeholder="Reset Token"
        tabindex="0"
      />
    </div>
    <div class="input-box">
      <p class="text">New Password</p>
      <input
        type="password"
        class="input--text"
        name="newPassword"
        v-model="newPassword"
        placeholder="New Password"
        tabindex="0"
      />
    </div>
    <div class="input-box">
      <p class="text">Confirm New Password</p>
      <input
        type="password"
        class="input--text"
        name="confirmPassword"
        v-model="confirmPassword"
        placeholder="Confirm new password"
        tabindex="0"
      />
    </div>
    <error-list v-if="errors.length" title="Errors:" v-bind:errors="errors" />
    <v-button
      :hierachyLevel="'primary'"
      :text="'Reset Password'"
      type="submit"
      tabindex="0"
    />
    <div v-if="newResetToken">
      <p class="text new-reset-token">
        New reset token: <span class="bold">{{ newResetToken }}</span>
      </p>
      <p class="text italics">
        Make sure to store this reset token somewhere safe.
      </p>
    </div>
  </form>
</template>

<script src="./ResetPasswordForm.js"></script>

<style lang="scss" src="./ResetPasswordForm.scss"></style>
