<template>
    <nav_links :links="links" class="nav_bar"/>

    <table>
        <thead>
            <tr>
                <th>Auction</th>
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
    .nav_bar {
        margin-bottom: 15px;
    }

    table {
        border-collapse: collapse;
        border: 1px solid #000;

        table-layout: fixed;
        width: 300px;
    }

    tbody > :deep(tr) {
        line-height: 28px;
        border: 1px solid #000;
    }

    th {
        padding: 10px;
        border-bottom: 1px solid #000;
        background-color: rgb(220,220,220)
    }
    th:nth-child(1) { width: 50%; }
</style>