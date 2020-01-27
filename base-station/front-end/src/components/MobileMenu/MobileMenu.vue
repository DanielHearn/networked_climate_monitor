<template>
  <div class="mobile-menu">
    <ul @click="toggleMenu">
      <router-link to="/" class="link">Home</router-link>
      <template v-if="!$store.state.user.logged_in">
        <router-link to="/login" class="link">Login</router-link>
        <router-link to="/register" class="link">Register</router-link>
      </template>
      <template v-if="$store.state.user.logged_in">
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
    </ul>
  </div>
</template>

<script src="./MobileMenu.js"></script>

<style lang="scss" src="./MobileMenu.scss"></style>
