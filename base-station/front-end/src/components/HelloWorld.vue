<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <p>
      For a guide and recipes on how to configure / customize this project,<br />
      check out the
      <a href="https://cli.vuejs.org" target="_blank" rel="noopener"
        >vue-cli documentation</a
      >.
    </p>
    <button @click="addFruit">Add fruit</button>
    <button @click="getFruit">Get fruit</button>
    <h3>Fruit in DB</h3>
    <ul v-if="fruits.length">
      <li v-for="(fruit, index) in fruits" :key="index">
        <p>{{fruit.type}} | {{fruit.count}}</p>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "HelloWorld",
  props: {
    msg: String
  },
  data: function() {
    return {
      fruits: []
    };
  },
  methods: {
    addFruit: function() {
      this.axios.post(`/api/fruit`)
    },
    getFruit: function() {
      this.axios.get(`/api/fruit`)
      .then(response => {
        this.fruits = response.data
      })
    }
  },
  mounted: function() {
    this.getFruit()
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "./../scss/variables.scss";

h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: $accent;
}
</style>
