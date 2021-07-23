<template>
    <tr v-if="visible">
        <td>{{bid.user}}</td>
        <td>{{value}}
            <span v-if="bid.is_proxy" class="proxy_string">
                (proxy)
            </span>
        </td>
        <td>{{elapsed}}</td>
    </tr>
</template>


<script>
    import { int_to_price } from "../../utils/misc_utils.js"

    export default {
        props: ['bid', 'visible'],
        inject: ['from_start'],

        computed: {
            value() {
                let ret= `${int_to_price(this.bid.bid)}`

                return ret
            },

            elapsed() {
                let diff= this.from_start(this.bid.time)

                let hours= Math.floor(diff / 3600)
                
                let min= diff % 3600
                min= Math.round(min / 60)

                return `+${hours}hr, ${min}min`
            }
        }
    }
</script>


<style scoped>
    td:nth-child(1) { width: 30% }
    td:nth-child(2) { width: 30% }

    .proxy_string {
        color: rgb(150,150,150);
    }
</style>