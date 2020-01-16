<template>
  <main-panel>
    <template slot="content">
      <div class="content-column">
        <h2 class="title">Introduction</h2>
        <p>
          The networked climate monitor project provides access to the recent
          and historical climate data from the sensors.
        </p>
        <p>
          This project has been designed and developed by Daniel Hearn for a
          final year project at the University of Portsmouth. The source code
          and designs for this project can be found on
          <a
            href="https://github.com/DanielHearn/networked_climate_monitor"
            class="link"
            >Github</a
          >
        </p>
        <p>
          To use the project the sensor nodes and base station must be setup,
          turned on and running their software. You must then register an
          account and login to this account. You can then access the climate
          data and manage sensors.
        </p>
        <p>
          <router-link to="/register" class="link"
            >To register click here</router-link
          >
          or
          <router-link to="/register" class="link"
            >click here to login</router-link
          >
          or
          <router-link to="/dashboard" class="link"
            >click here to view the dashboard.</router-link
          >
        </p>
      </div>
    </template>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'

export default {
  name: 'home',
  components: {
    MainPanel
  }
}
</script>
