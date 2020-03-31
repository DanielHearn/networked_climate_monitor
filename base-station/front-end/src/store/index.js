import Vue from 'vue'
import Vuex from 'vuex'
import { getAccount } from './../static/api'

Vue.use(Vuex)

export const mutations = {
  setMobile(state, value) {
    Vue.set(state, 'mobile', value)
  },
  setMobileMenu(state, value) {
    Vue.set(state, 'mobileMenu', value)
  },
  setUser(state, value) {
    Vue.set(state, 'user', value)
  }
}

export const getters = {
  mobile: state => state.mobile,
  mobileMenu: state => state.mobileMenu,
  user: state => state.user
}

export const actions = {
  /**
   * Update the user's reset token
   * @param {string} resetToken - User's reset token
   */
  updateResetToken({ commit, state }, resetToken) {
    const user = state.user
    user.reset_token = resetToken
    commit('setUser', user)
  },
  /**
   * Update the user details
   * @param {object} data - User details
   * @param {boolean} doRetrieveAcc - Whether user details should be retrieved from the API
   */
  login({ commit }, data) {
    commit('setUser', data)
  },
  /**
   * Update the user details and retrieve user details from the API
   * @param {object} data - User details
   */
  register({ commit, dispatch }, data) {
    commit('setUser', data)
    dispatch('retrieveAccount', data.access_token)
  },
  /**
   * Clear user details
   */
  logout({ commit, state }) {
    const user = state.user

    user.logged_in = false
    user.access_token = ''
    user.refresh_token = ''
    user.email = ''

    commit('setUser', user)
  },
  /**
   * Retrieve user details from the API
   * @param {string} accessToken - User's access token
   */
  retrieveAccount({ commit, state }, accessToken) {
    getAccount(accessToken)
      .then(response => {
        const data = response.data
        if (data.status && data.account) {
          const user = state.user
          user.email = data.account.email
          user.reset_token = data.account.reset_token
          user.settings = JSON.parse(data.account.settings.replace(/'/g, '"'))

          commit('setUser', user)
        }
      })
      .catch(e => {
        console.warn(e)
      })
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
  getters,
  mutations,
  actions
}

export default new Vuex.Store(storeConfig)
