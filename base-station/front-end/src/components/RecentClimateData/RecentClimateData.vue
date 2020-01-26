<template>
  <ul class="recent-data-list">
    <li v-for="(data, index) in climateData" :key="index">
      <p class="text">{{ data.type }}</p>
      <p class="sub-heading">
        {{ data.formattedText }}
      </p>
    </li>
  </ul>
</template>

<script src="./RecentClimateData.js"></script>

<style lang="scss" src="./RecentClimateData.scss"></style>
