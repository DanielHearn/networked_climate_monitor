<template>
  <ul class="recent-data-list">
    <li v-for="(data, index) in climateData" :key="index">
      <p class="text">{{ data.type }}</p>
      <p class="sub-heading">
        {{ data.formattedText }}
      </p>
      <p v-if="data.one_day_high" class="text">
        Today's High:
        {{ data.one_day_high }}
      </p>
      <p v-if="data.one_day_low" class="text">
        Today's Low: {{ data.one_day_low }}
      </p>
    </li>
  </ul>
</template>

<script src="./RecentClimateData.js"></script>

<style lang="scss" src="./RecentClimateData.scss"></style>
