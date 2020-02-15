<template>
  <div class="mobile-menu">
    <ul @click="toggleMenu">
      <router-link to="/" class="link">Home</router-link>
      <template v-if="!loggedIn">
        <router-link to="/login" class="link">Login</router-link>
        <router-link to="/register" class="link">Register</router-link>
      </template>
      <template v-if="loggedIn">
        <router-link to="/dashboard" v-if="loggedIn" class="link"
          >Dashboard</router-link
        >
        <router-link to="/settings" v-if="loggedIn" class="link"
          >Settings</router-link
        >
      </template>
    </ul>
  </div>
</template>

<script src="./MobileMenu.js"></script>

<style lang="scss" src="./MobileMenu.scss"></style>
