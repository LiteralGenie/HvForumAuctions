<template>
    <proxy_view/>
</template>

<script>
import proxy_view from "../../components/proxy_view.vue"

export default {
    name: 'App',
    components: {
        proxy_view
    },

    created() {
        document.querySelector("#loading").remove()
    }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
