<template>
    <basic_body_row
    :item="item"
    :transforms="transforms">
        <b>{{ int_to_price(item.proxy_bid) }}</b>
    </basic_body_row>
</template>

<script>
    import basic_body_row from "./basic_body_row.vue"

    export default {
        props: ["item"],
        inject: ["int_to_price"],

        data() { return {
            transforms: {
                current_bid: this.int_to_price,
            },
        }},

        components: {
            basic_body_row
        },
    }
</script>

<style scoped>

</style>