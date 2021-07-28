<template>
    <div class="root">
        <!-- bid confirmed -->
        <nav_links :links="links" class="nav_bar"/>

        <div class="summary">
            <div id="title"><a :href="ctx.auction_link">{{ctx.auction_name}}</a></div>
            <span v-if="ctx.is_current">
                <b>Last Update:</b> {{last_update}}<br/>
            </span>
            <span><b>Auction Start:</b> {{fmt_time(ctx.start)}}</span><br/>
            <span><b>Auction End:</b> {{fmt_time(ctx.end)}}</span>
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
        <img v-if="ctx.is_current"
        :src="timer_url">
    </div>
</template>

<script>
    import item_row from "./item_row.vue"
    import nav_links from "../navigation.vue"

    export default {
        data() { return {
            ctx: null,

            last_update: 0,
            links: []
        }},

        created() {
            this.ctx= this.init_ctx()
            
            this.links= [
                {text: "all logs", href: "/logs"},
                {text: "auction link", href: this.ctx.auction_link},
            ]
            console.log(this.links)

            setInterval(() => {
                this.refresh_last_update()
            }, 400);
        },

        methods: {
            // data initialization
            init_ctx() {
                let ctx= JSON.parse(JSON.stringify(this.RESP_DATA))
                return ctx
            },

            
            from_start(t) {
                return t - this.ctx.start
            },

            fmt_time(t) {
                let pad= (x => String(x).padStart(2,0))
                let month_list= ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                
                let offset= 60*1000*new Date().getTimezoneOffset()
                let d= new Date(t*1000 + offset)

                let day= d.getDate()
                let month= month_list[d.getMonth()]
                let hour= d.getHours()
                let min= d.getMinutes()

                return `${pad(month)}-${pad(day)}, ${pad(hour)}:${pad(min)} UTC`
            },

            refresh_last_update() {
                let pad= (x => String(x).padStart(2,0))
                let total_seconds= Math.round(Date.now()/1000 - this.ctx.last_update)

                let minutes= Math.floor(total_seconds / 60)
                let seconds= total_seconds % 60

                let ret= []
                if(minutes) ret.push(`${minutes}m`)
                ret.push(`${seconds}s`)
                ret.push('ago')

                this.last_update= ret.join(' ')
            }
        },

        computed: {
            timer_url() { 
                return "https://auction.e33.moe/timer#.png";
                return process.env.VUE_APP_SERVER_URL + "/timer" 
            },
        },

        provide() { return {
            from_start: this.from_start
        }},

        components: {
            item_row,
            nav_links,
        }
    }
</script>


<style scoped>
    .root {
        display: grid;
    }

    .summary {
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

    .nav_bar {
        margin-bottom: 10px;
    }
</style>