<template>
  <div class="main-panel">
    <div class="main-panel-header">
      <slot name="header"></slot>
    </div>
    <div class="main-panel-content">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script src="./MainPanel.js"></script>

<style lang="scss" src="./MainPanel.scss"></style>
