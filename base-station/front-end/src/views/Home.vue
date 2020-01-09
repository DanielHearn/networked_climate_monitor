<template>
  <main-panel>
    <div>
      <h2>Introduction</h2>
      <p>The networked climate monitor project provides access to the recent and historical climate data for the sensors.</p>
      <p>To access the climate data an account will need to be registered</p>
    </div>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'

export default {
  name: "home",
  components: {
    MainPanel
  }
};
</script>
