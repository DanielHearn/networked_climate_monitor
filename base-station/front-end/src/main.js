import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

import Toasted from 'vue-toasted';
import axios from 'axios'
import VueAxios from 'vue-axios'
Vue.use(VueAxios, axios)
Vue.use(Toasted, {
  action : {
      text : 'Close',
      onClick : (e, toastObject) => {
          toastObject.goAway(0);
      }
  },
  position: 'bottom-right',
  duration: 5000,
  keepOnHover: true
})
Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
