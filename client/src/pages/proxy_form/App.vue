<template>
    <proxy_form/>
</template>

<script>
import proxy_form from "../../components/proxy_form/_main.vue"

export default {
    name: 'App',
    components: {
        proxy_form
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
