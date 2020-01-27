<template>
  <div class="nav">
    <div class="nav__side nav__left">
      <router-link to="/" class="link title--nav" v-if="!$store.state.mobile"
        >Climate Monitor</router-link
      >
      <logout-button v-else />
    </div>
    <div class="nav__links">
      <template v-if="!$store.state.mobile">
        <router-link to="/" class="link">Home</router-link>
        <router-link
          to="/login"
          v-if="!$store.state.user.logged_in"
          class="link"
          >Login</router-link
        >
        <router-link
          to="/register"
          v-if="!$store.state.user.logged_in"
          class="link"
          >Register</router-link
        >
        <router-link
          to="/dashboard"
          v-if="$store.state.user.logged_in"
          class="link"
          >Dashboard</router-link
        >
        <router-link
          to="/settings"
          v-if="$store.state.user.logged_in"
          class="link"
          >Settings</router-link
        >
      </template>
    </div>
    <div class="nav__side nav__right">
      <logout-button
        v-if="$store.state.user.logged_in && !$store.state.mobile"
      />
      <v-button
        v-if="$store.state.mobile"
        @click.native="toggleMenu"
        :hierachyLevel="'secondary'"
        :text="$store.state.mobileMenu ? 'close' : 'menu'"
        :isIcon="true"
        style="margin-left: 2em;"
      />
    </div>
  </div>
</template>

<script src="./Nav.js"></script>

<style lang="scss" src="./Nav.scss"></style>
