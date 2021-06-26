<template>
    <basic_body_row
    :item="item"
    @click="update_model" 
    :class="{selected: item.selected}">
        <input type="checkbox" v-model="item.selected">
    </basic_body_row>
</template>

<script>
    import basic_body_row from "./basic_body_row.vue"
    
    export default {
        props: ["item"],
        emits: ["update:item"],

        methods: {
            update_model() {
                let ret= Object.assign({}, this.item)
                ret.selected= !ret.selected
                this.$emit("update:item", ret)
            },
        },
        
        components: {
            basic_body_row,
        },
    }
</script>

<style scoped>
</style>