<template>
    <div id="root">
        <div id="summary">
            <div id="title"><a :href="ctx.auction_link">Genie's Bottle #4</a></div>
            <span><b>Last Update:</b> 52s ago</span>
            <br/><span><b>Auction Start:</b> {{start_time}}</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th/>
                    <th>Item Code</th>
                    <th>Item Name</th>
                    <th>Current Bid</th>
                </tr>
            </thead>
            <tbody>
                <item_row
                v-for="(item,i) in ctx.items"
                :item="ctx.items[i]"/>
            </tbody>
        </table>
        <img :src="timer_url">
    </div>
</template>

<script>
    import item_row from "./item_row.vue"

    export default {
        data() { return {
            ctx: null
        }},

        created() {
            this.ctx= this.init_ctx()
        },

        methods: {
            // data initialization
            init_ctx() {
                let ctx= JSON.parse(JSON.stringify(this.RESP_DATA))
                return ctx
            },

            
            from_start(t) {
                return t - this.ctx.start
            }
        },

        computed: {
            timer_url() { 
                return "https://auction.e33.moe/timer#.png";
                return process.env.VUE_APP_SERVER_URL + "/timer" 
            },
            start_time() {
                let month_list= ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                
                let d= new Date(this.ctx.start*1000)
                let day= d.getDate()
                let month= month_list[d.getMonth()]
                let hour= d.getHours()
                let min= d.getMinutes()

                return `${month}-${day}, ${hour}:${min} UTC`
            }
        },

        provide() { return {
            from_start: this.from_start
        }},

        components: {
            item_row,
        }
    }
</script>


<style scoped>
    #root {
        display: grid;
    }

    #summary {
        text-align: left;
        line-height: 20px;
        margin-bottom: 20px;
    }

    img {
        align-self: left;
        margin-top: 30px;
    }

    #title {
        padding-bottom: 2px;
    }

    table {
        border-collapse: collapse;
        border: 1px solid #000;

        table-layout: fixed;
        width: 1000px;
    }

    th:nth-child(1) { width: 8%; }
    th:nth-child(2) { width: 10%; }
    th:nth-child(4) { width: 20%; }

    th {
        padding: 10px;
        border-bottom: 1px solid #000;
        background-color: rgb(220,220,220)
    }
</style>