import Vue from 'vue'
import Vuex from 'vuex'

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
  logout({ commit, state }) {
    const user = state.user

    user.logged_in = false
    user.access_token = ''
    user.refresh_token = ''
    user.email = ''
    commit('setUser', user)
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
