<template>
        </li>
  <div class="content">
    <side-panel
      v-if="
        !$store.state.mobile || ($store.state.mobile && activeCategoryID === -1)
      "
    >
      <template slot="header">
        <p class="sub-heading">Settings Categories</p>
      </template>
      <template slot="content">
        <ul class="list">
          <li
            class="list-item"
            v-bind:class="{ active: activeCategoryID === 0 }"
            style="display: flex; flex-direction: column; justify-content: flex-start; text-align: left;"
          >
            <template>
              <div style="display: flex; flex-direction: row;">
                <p
                  class="heading"
                  style="margin-right: 0.25em; display: flex; align-items: center;"
                  :class="{
                    underline: activeCategoryID === 0
                  }"
                >
                  Measurement Settings
                </p>
              </div>
              <div class="actions">
                <v-button
                  @click.native="activeCategoryID = 0"
                  :type="'primary'"
                  :text="'Edit settings'"
                />
              </div>
            </template>
          </li>
          <li
            class="list-item"
            v-bind:class="{ active: activeCategoryID === 1 }"
            style="display: flex; flex-direction: column; justify-content: flex-start; text-align: left;"
          >
            <template>
              <div style="display: flex; flex-direction: row;">
                <p
                  class="heading"
                  style="margin-right: 0.25em; display: flex; align-items: center;"
                  :class="{
                    underline: activeCategoryID === 1
                  }"
                >
                  Account Management
                </p>
              </div>
              <div class="actions">
                <v-button
                  @click.native="activeCategoryID = 1"
                  :type="'primary'"
                  :text="'Manage account'"
                />
              </div>
            </template>
          </li>
        </ul>
      </template>
    </side-panel>
    <template
      v-if="
        !$store.state.mobile || ($store.state.mobile && activeCategoryID !== -1)
      "
    >
      <main-panel>
        <template v-if="activeCategoryID === 0">
          <template slot="header">
            <p class="sub-heading">Measurement Settings</p>
          </template>
          <template slot="content">
            <div class="dashboard-content">
              <v-button
                v-if="$store.state.mobile"
                @click.native="activeCategoryID = -1"
                :type="'tertiary'"
                :text="'Back'"
              />
              <p v-if="!$store.state.user.logged_in">Please log in</p>
              <ul>
                <li
                  v-for="(setting, key) in this.$store.state.user.settings"
                  :key="key"
                >
                  <p>{{ key }}: {{ setting }}</p>
                </li>
              </ul>
            </div>
          </template>
        </template>
        <template v-if="activeCategoryID === 1">
          <template slot="header">
            <p class="sub-heading">Account Management</p>
          </template>
          <template slot="content">
            <div class="dashboard-content">
              <v-button
                v-if="$store.state.mobile"
                @click.native="activeCategoryID = -1"
                :type="'tertiary'"
                :text="'Back'"
              />
              <p>LINK</p>
            </div>
          </template>
        </template>
      </main-panel>
    </template>
  </div>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import SidePanel from './../components/SidePanel/SidePanel.vue'
import vButton from './../components/vButton/vButton.vue'
import { HTTP } from './../static/http-common'

export default {
  name: 'settings',
  components: {
    MainPanel,
    SidePanel,
    vButton
  },
  data: function() {
    return {
      activeCategoryID: -1
    }
  },
  methods: {
    loadSettings: function() {
      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        HTTP.get('account', {
          headers: { Authorization: 'Bearer ' + accessToken }
        })
          .then(response => {
            const data = response.data
            if (data.status && data.account) {
              const user = this.$store.state.user
              user.settings = JSON.parse(
                data.account.settings.replace(/'/g, '"')
              )

              this.$store.commit('setUser', user)
            }
          })
          .catch(e => {
            if (e.response && e.response.data) {
              this.$router.push('/login')
            }
          })
      } else {
        this.$router.push('/login')
      }
    }
  },
  created: function() {
    console.log('Load settings')
    if (!this.$store.state.mobile) {
      this.activeCategoryID = 0
    }

    if (this.$store.state.user.logged_in) {
      this.loadSettings()
    } else {
      setTimeout(() => {
        this.loadSettings()
      }, 150)
    }
  }
}
</script>
