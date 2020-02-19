<template>
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
                  :hierachyLevel="'primary'"
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
                  :hierachyLevel="'primary'"
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
                :hierachyLevel="'tertiary'"
                :text="'Back'"
                class="back-button"
              />
              <p v-if="!$store.state.user.logged_in">Please log in</p>
              <template v-else-if="settings">
                <div class="input-box" v-if="settings.temperature_unit">
                  <p class="sub-heading">Temperature Unit:</p>
                  <div class="radio-container">
                    <div
                      class="radio-option"
                      :class="{ active: settings.temperature_unit === 'c' }"
                    >
                      <label for="temp_unit_c"
                        >Celsius
                        <input
                          type="radio"
                          id="temp_unit_c"
                          value="c"
                          v-model="settings.temperature_unit"
                          class="radio"/>
                        <span class="input">
                          <i
                            v-if="settings.temperature_unit === 'c'"
                            class="material-icons"
                            >done</i
                          >
                          <i v-else class="material-icons"></i> </span
                      ></label>
                    </div>
                    <div
                      class="radio-option"
                      :class="{ active: settings.temperature_unit === 'f' }"
                    >
                      <label for="temp_unit_f"
                        >Farenheit
                        <input
                          type="radio"
                          id="temp_unit_f"
                          value="f"
                          v-model="settings.temperature_unit"
                          class="radio"/>
                        <span class="input">
                          <i
                            v-if="settings.temperature_unit === 'f'"
                            class="material-icons"
                            >done</i
                          >
                          <i v-else class="material-icons"></i> </span
                      ></label>
                    </div>
                  </div>
                  <p
                    class="text italics"
                    v-if="settings.temperature_unit === 'c'"
                  >
                    Temperatures are stored in celsius and will be displayed in
                    celsius.
                  </p>
                  <p class="text italics" v-else>
                    Temperatures are stored in celsius and will be displayed in
                    farenheit
                  </p>
                </div>
              </template>
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
                :hierachyLevel="'tertiary'"
                :text="'Back'"
              />
              <div class="settings-box">
                <p class="sub-heading">Change Password</p>
                <router-link to="/reset-password" class="link"
                  >Change Password</router-link
                >
                <p class="text italics">
                  This reset token can be used to reset the account password on
                  the password reset page, make sure it is saved somewhere
                  secure.
                </p>
                <p class="text">
                  Reset Token:
                  <span class="bold">{{ $store.state.user.reset_token }}</span>
                </p>
              </div>
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
import { getAccount, patchAccount } from './../static/api'
import { cloneDeep } from 'lodash'

export default {
  name: 'settings',
  components: {
    MainPanel,
    SidePanel,
    vButton
  },
  data: function() {
    return {
      activeCategoryID: -1,
      settings: {},
      hasBeenEdited: false
    }
  },
  watch: {
    settings: {
      handler(newSettings) {
        if (this.hasBeenEdited && Object.keys(newSettings).length) {
          const user = cloneDeep(this.$store.state.user)
          user.settings = Object.assign({}, newSettings)
          this.$store.commit('setUser', user)
          this.updateSettings()
        }
        if (!this.hasBeenEdited) {
          this.hasBeenEdited = true
        }
      },
      deep: true
    }
  },
  methods: {
    loadSettings: function() {
      const accessToken = this.$store.state.user.access_token
      if (accessToken) {
        getAccount(accessToken)
          .then(response => {
            const data = response.data
            if (data.status && data.account) {
              const user = cloneDeep(this.$store.state.user)
              user.settings = JSON.parse(
                data.account.settings.replace(/'/g, '"')
              )
              this.settings = user.settings
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
    },
    updateSettings: function() {
      const accessToken = this.$store.state.user.access_token
      const stringifiedSettings = JSON.stringify(this.settings)

      patchAccount(accessToken, { settings: stringifiedSettings })
        .then(response => {
          const data = response.data
          if (data.status) {
            this.$toasted.show('Settings updated')
          }
        })
        .catch(e => {
          console.warn(e)
        })
    }
  },
  created: function() {
    if (!this.$store.state.mobile) {
      this.activeCategoryID = 0
    }
    if (Object.keys(this.$store.state.user.settings).length) {
      this.settings = this.$store.state.user.settings
    } else {
      setTimeout(() => {
        this.loadSettings()
      }, 25)
    }
  }
}
</script>
