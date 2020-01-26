<template>
  <form id="login" class="form" @submit="checkLogin" method="post">
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
    <router-link to="/reset-password" class="link" tabindex="-1"
      >Forgotten your password? Click here</router-link
    >
    <error-list v-if="errors.length" title="Errors:" v-bind:errors="errors" />
    <v-button
      :hierachyLevel="'primary'"
      :text="'Login'"
      type="submit"
      value="Submit"
      tabindex="0"
    />
    <router-link to="/register" class="link"
      >Not registered? Click here to register</router-link
    >
  </form>
</template>

<script src="./LoginForm.js"></script>

<style lang="scss" src="./LoginForm.scss"></style>
