<template>
    <div class="nav-root">
        <template v-for="(l,i) in links">
            <a :href="l.href">{{l.text}}</a>
            <span v-if="i!==links.length-1"
            class="sep">
                •
            </span>
        </template>
    </div>
</template>

<script>
    export default {
        props: ["links"]
    }
</script>

<style scoped>
.nav-root {
    display: flex;
    justify-content: left
}

.sep {
    margin: 0px 5px 0px 5px
}
</style>