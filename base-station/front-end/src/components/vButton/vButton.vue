<template>
  <button :class="['button', typeClass]">
    <template v-if="isIcon">
      <i class="material-icons">{{ text }}</i>
    </template>
    <template v-else>{{ text }}</template>
  </button>
</template>

<script src="./vButton.js"></script>

<style lang="scss" src="./vButton.scss"></style>
