import Vue from 'vue'
import Vuex from 'vuex'

import { setStoredAccessToken, setStoredRefreshToken } from './storage.js'

Vue.use(Vuex)

export const mutations = {
  setMobile(state, value) {
    state.mobile = value
  },
  setMobileMenu(state, value) {
    state.mobileMenu = value
  },
  setUser(state, value) {
    state.user = value
    setStoredAccessToken(value.access_token)
    setStoredRefreshToken(value.refresh_token)
  }
}

export const storeConfig = {
  state: {
    mobile: false,
    mobileMenu: false,
    user: {
      access_token: '',
      refresh_token: '',
      logged_in: false,
      email: '',
      settings: {}
    }
  },
  mutations: mutations
}

export default new Vuex.Store(storeConfig)
