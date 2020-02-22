<template>
  <ul class="recent-data-list">
    <li v-for="(data, index) in climateData" :key="index">
      <p class="text">{{ data.type }}</p>
      <p class="sub-heading">
        {{ data.formattedText }}
      </p>
      <p v-if="data.previousValue && data.trendDirection" class="trend">
        <i class="material-icons">{{ data.trendDirectionIcon }}</i>
        {{ data.previousValue }}
      </p>
      <p v-if="data.oneDayHigh" class="text one-day-high">
        High:
        {{ data.oneDayHigh }}
      </p>
      <p v-if="data.oneDayLow" class="text one-day-low">
        Low: {{ data.oneDayLow }}
      </p>
    </li>
  </ul>
</template>

<script src="./RecentClimateData.js"></script>

<style lang="scss" src="./RecentClimateData.scss"></style>
