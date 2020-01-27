<template>
  <form id="register" class="form" @submit="checkRegister" method="post">
    <div class="input-box">
      <p class="text">Email</p>
      <input
        type="email"
        class="input--text"
        name="email"
        v-model="email"
        placeholder="Email"
        tabindex="0"
      />
    </div>
    <div class="input-box">
      <p class="text">Password</p>
      <input
        type="password"
        class="input--text"
        name="password"
        v-model="password"
        placeholder="Password"
        tabindex="0"
      />
    </div>
    <div class="input-box">
      <p class="text">Confirm Password</p>
      <input
        type="password"
        class="input--text"
        name="confirmPassword"
        v-model="confirmPassword"
        placeholder="Confirm password"
        tabindex="0"
      />
    </div>
    <error-list v-if="errors.length" title="Errors:" v-bind:errors="errors" />
    <v-button
      :hierachyLevel="'primary'"
      :text="'Register'"
      type="submit"
      tabindex="0"
    />
  </form>
</template>

<script src="./RegisterForm.js"></script>

<style lang="scss" src="./RegisterForm.scss"></style>
