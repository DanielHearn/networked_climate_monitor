<template>
  <div class="nav">
    <div class="nav__side nav__left">
      <router-link to="/" class="link title--nav" v-if="!mobile"
        >Climate Monitor</router-link
      >
      <v-button
        v-else-if="loggedIn"
        @click.native="logout"
        class="logout-button"
        :hierachyLevel="'secondary'"
        :text="'person'"
        :isIcon="true"
      />
    </div>
    <div class="nav__links">
      <template v-if="!mobile">
        <router-link to="/" class="link">Home</router-link>
        <router-link to="/login" v-if="!loggedIn" class="link"
          >Login</router-link
        >
        <router-link to="/register" v-if="!loggedIn" class="link"
          >Register</router-link
        >
        <router-link to="/dashboard" v-if="loggedIn" class="link"
          >Dashboard</router-link
        >
        <router-link to="/settings" v-if="loggedIn" class="link"
          >Settings</router-link
        >
      </template>
    </div>
    <div class="nav__side nav__right">
      <v-button
        v-if="loggedIn && !mobile"
        @click.native="logout"
        class="logout-button"
        :hierachyLevel="'secondary'"
        :text="'person'"
        :isIcon="true"
        style="margin-left: 2em;"
      />
      <v-button
        v-if="mobile"
        class="mobile-menu-button"
        @click.native="toggleMenu"
        :hierachyLevel="'secondary'"
        :text="mobileMenu ? 'close' : 'menu'"
        :isIcon="true"
        style="margin-left: 2em;"
      />
    </div>
  </div>
</template>

<script src="./Nav.js"></script>

<style lang="scss" src="./Nav.scss"></style>
