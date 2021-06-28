<template>
    <form @submit.prevent="submit">
        <!-- bid table -->
        <span class="instructions">Please confirm your bids.</span>
        <table>
            <basic_thead>
                Your Bid
            </basic_thead>
            <tbody>
                <confirm_row
                v-for="i in filter_selected(ctx)"
                v-model:item="ctx.items[i]"/>
            </tbody>
        </table>
        
        <!-- username -->
        <span class="user">Username: <b>{{ctx.user}}</b></span>
        
        <!-- submit button -->
        <button 
        :disabled="disabled">
            <span v-if="!disabled">Request bid code</span>
            <span v-if="disabled">Waiting for server...</span>
        </button>
    </form>
</template>

<script>
    import basic_thead from "./basic_thead.vue"
    import confirm_row from "./confirm_row.vue"
    
    export default {
        props: ["ctx"],
        inject: ["filter_selected", "set_status"],

        data() { return {
            disabled: false
        }},

        methods: {
            async submit() {
                this.disabled= true
                this.set_status("", "bid_code_request", { level:"critical" })

                let payload= this.get_payload(this.ctx)
                console.log('sending', payload)
                let resp= await this.$http.post(process.env.VUE_APP_SERVER_URL + "/api/proxy/form", payload)
                console.log('response', resp)

                // window.location.href= process.env.VUE_APP_SERVER_URL + "/proxy/view?key=" + resp.data.key
            },

            get_payload(ctx) {
                let ret= {}

                // user
                ret.user= ctx.user

                // bids
                ret.items= []
                ctx.items.filter(it => it.selected).forEach(it => {
                    let tmp= {}
                    tmp.cat= it.cat
                    tmp.code= it.code
                    tmp.bid= it.proxy_bid * process.env.VUE_APP_SCALE_FACTOR

                    ret.items.push(tmp)
                })

                // return
                return ret
            },
        },

        components: {
            basic_thead,
            confirm_row,
        },
    }
</script>

<style scoped>
    >>>td:nth-child(3), >>>th:nth-child(3),
    >>>td:nth-child(1), >>>th:nth-child(1) {
        color: rgba(0,0,0, 0.5)
    }

    .user {
        font-size: 15px;
        margin-top: 20px;
    }

    button {
        font-size: 15px;
        font-weight: bold;
        padding: 0 10px 0 10px;
        height: 30px;
        margin-top: 20px;
        justify-self: center;
    }
</style>