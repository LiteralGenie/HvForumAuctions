<template>
    <nav_links :links="links" class="nav_bar"/>

    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Start Date</th>
            </tr>
        </thead>
        <tbody>
            <row v-for="log in ctx.logs" :log="log"/>
        </tbody>
    </table>
</template>

<script>
    import { int_to_price } from "../../utils/misc_utils.js"
    import nav_links from "../navigation.vue"
    import row from "./row.vue"

    export default {
        data() { return {
            ctx: null,

            links: []
        }},

        created() {
            // load pre-fetched api response
            this.ctx= JSON.parse(JSON.stringify(this.RESP_DATA))

            this.links= [
                { text: "auction info", href: this.ctx.info_link }
            ]
        },

        components: {
            nav_links,
            row,
        }
    }
</script>

<style scoped>
</style>