<template>
  <div class="side-panel">
    <div class="side-panel-header">
      <slot name="header"></slot>
    </div>
    <div class="side-panel-content">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script src="./SidePanel.js"></script>

<style lang="scss" src="./SidePanel.scss"></style>
