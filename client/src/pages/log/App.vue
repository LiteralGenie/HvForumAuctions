<template>
    <log/>
</template>

<script>
import log from "../../components/log/main.vue"

export default {
    name: 'App',
    components: {
        log
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
