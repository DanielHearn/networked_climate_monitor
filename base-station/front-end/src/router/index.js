import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";

Vue.use(VueRouter);

const titleEnd = ' - Climate Monitor'

const routes = [
  {
    path: "/",
    name: "home",
    component: Home,
    meta: {
      title: () => {
        return `Home${titleEnd}`
      },
    },
  },
  {
    path: "/login",
    name: "login",
    component: () =>
      import(/* webpackChunkName: "login" */ "../views/Login.vue"),
    meta: {
      title: () => {
        return `Login${titleEnd}`
      },
    },
  },
  {
    path: "/register",
    name: "register",
    component: () =>
      import(/* webpackChunkName: "register" */ "../views/Register.vue"),
    meta: {
      title: () => {
        return `Register${titleEnd}`
      },
    },
  },
  {
    path: "/reset-password",
    name: "resetpassword",
    component: () =>
      import(/* webpackChunkName: "resetpassword" */ "../views/ResetPassword.vue"),
    meta: {
      title: () => {
        return `Reset Password${titleEnd}`
      },
    },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () =>
      import(/* webpackChunkName: "dashboard" */ "../views/Dashboard.vue"),
    meta: {
      title: () => {
        return `Dashboard${titleEnd}`
      },
    },
  },
  {
    path: "/settings",
    name: "settings",
    component: () =>
      import(/* webpackChunkName: "settings" */ "../views/Settings.vue"),
    meta: {
      title: () => {
        return `Settings${titleEnd}`
      },
    },
  },
  {
    path: '*',
    component: () =>
    import(/* webpackChunkName: "notfound" */ "../views/NotFound.vue"),
    meta: {
      title: () => {
        return `404 Not Found${titleEnd}`
      },
    }
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;

router.afterEach((to) => {
  Vue.nextTick(() => {
    document.title = to.meta.title(to)
  })
})
