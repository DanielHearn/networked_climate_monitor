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
  login({ commit, dispatch }, data, doRetrieveAcc) {
    commit('setUser', data)

    if (doRetrieveAcc) {
      dispatch('retrieveAccount', data.access_token)
    }
  },
  register({ commit, dispatch }, data) {
    commit('setUser', data)
    dispatch('retrieveAccount', data.access_token)
  },
  logout({ commit, state }) {
    const user = state.user

    user.logged_in = false
    user.access_token = ''
    user.refresh_token = ''
    user.email = ''

    commit('setUser', user)
  },
  retrieveAccount({ commit, state }, accessToken) {
    getAccount(accessToken)
      .then(response => {
        const data = response.data
        if (data.status && data.account) {
          const user = state.user
          user.email = data.account.email
          user.access_token = data.account.access_token
          user.refresh_token = data.account.refresh_token
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
