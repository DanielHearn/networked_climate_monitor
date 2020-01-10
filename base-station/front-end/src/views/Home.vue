<template>
  <main-panel>
    <template slot="content">
      <div>
        <h2 class="title">Introduction</h2>
        <p>The networked climate monitor project provides access to the recent and historical climate data for the sensors.</p>
        <p>To access the climate data an account will need to be registered</p>
      </div>
      <div>
        <p>Source code on <a href="https://github.com/DanielHearn/networked_climate_monitor" class="link">Github</a>.</p>
      </div>
    </template>
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
