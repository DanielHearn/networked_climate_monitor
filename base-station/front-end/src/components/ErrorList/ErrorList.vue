<template>
  <div class="error-list">
    <p v-if="title" class="title">{{ title }}</p>
    <ul>
      <li v-for="(error, index) in errors" :key="index">
        <p>{{ error }}</p>
      </li>
    </ul>
  </div>
</template>

<script src="./ErrorList.js"></script>

<style lang="scss" src="./ErrorList.scss"></style>
