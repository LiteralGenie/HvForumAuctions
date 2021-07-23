<template>
    <div>
        <nav_links :links="links" class="nav_bar"/>

        <!-- bid confirmed -->
        <div id="confirmation">
            <div id="summary">
                <div>username: <b>{{ctx.user}}</b></div>
                <div>bid code: <b>{{ctx.code}}</b></div>
                <div>bid date: <b>{{start_time}}</b></div>
            </div>
            
            <div
            v-if="ctx.confirmed">
                (Your bids have been placed!)
            </div>

            <div
            class="unconfirmed"
            v-if="!ctx.confirmed">
                <div>
                    Your proxy bids will not be placed until you reply to the 
                    <a :href="ctx.thread">auction thread</a>
                    with your bid code (<b>{{ctx.code}}</b>).
                    <br>
                </div>

                <div id="button_div">
                    <button
                    :disabled="disabled"
                    @click="do_check">
                        {{button_text}}
                    </button>
                    <br>
                    <img 
                    v-if="disabled"
                    :src="load_image" width="150"/>
                </div>
            </div>
        </div>

        <!-- items -->
        <hr id="item_rule">
        <table :class="{unconfirmed: !ctx.confirmed}">
            <thead>
                <tr>
                    <th>Item Code</th>
                    <th>Item</th>
                    <th>Your Proxy Bid</th>
                    <th>Winning Bid</th>
                </tr>
            </thead>
            <tbody>
                <tr 
                v-for="it in ctx.items"
                :class="{losing: !is_winning(it)}">
                    <td>{{ get_item_code(it) }}</td>
                    <td v-html="get_item_link(it)"/>
                    <td>{{ itp(it.bid) }}</td>
                    <td>
                        <div v-if="is_winning(it)">
                            {{ itp(it.winner.bid) }}
                            <br>(yours)
                        </div>
                        <div v-if="!is_winning(it)">
                            {{ itp(it.winner.bid) }}
                            <span v-if="it.winner.user">
                                <br>({{ it.winner.user }})
                            </span>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
    import { int_to_price } from "../utils/misc_utils.js"
    import nav_links from "./navigation.vue"

    export default {
        data() { return {
            ctx: null,

            lock_time: 0,
            cooldown: 0,
            disabled: false,
            load_image: this.get_load_image(),

            links: [{text: "bid log", href: "/"}],
        }},

        created() {
            // load pre-fetched api response
            this.ctx= JSON.parse(JSON.stringify(this.RESP_DATA))

            console.log(this.links, 'wtf')
            this.links= [
                {text: "bid log", href: "/"},
                {text: "auction thread", href: this.ctx.thread},
            ]
            console.log(this.links, 'wtf')
        },

        methods: {
            itp(x) {
                return int_to_price(x,1)
            },

            get_item_link(item) {
                if(item.link)
                    return `<a @click.stop target="_blank" href="${item.link}">${item.name}</a>`
                else
                    return `${item.name}`
            },

            get_item_code(item) {
                return `${item.cat}_${item.code}`
            },

            is_winning(item) {
                return item.winner.user === this.ctx.user
            },

            async do_check() {
                let check_url= process.env.VUE_APP_SERVER_URL + "/api/update_check"
                
                // all outcomes will reload the page, so disable button until then
                this.disabled= true
                this.load_image= this.get_load_image()

                // get cooldown
                let cd= (await this.$http.get(check_url)).data.cooldown
                cd= parseInt(cd)
                console.assert(!isNaN(cd))
                
                // do update if possible
                if(cd <= 0) {
                    console.log('updating')
                    await this.do_update()

                // else set button cooldown
                } else {
                    console.log('waiting', cd)
                    this.lock_time= cd + Date.now()/1000
                    this.start_cooldown()
                }
            },

            async do_update() {
                console.log('requesting update')
                let update_url= process.env.VUE_APP_SERVER_URL + "/update?no_redirect=1"
                await this.$http.get(update_url)
                location.reload()
            },

            start_cooldown() {
                this.cooldown= this._cooldown()

                // keep checking until ready
                if(this.cooldown > 0) {
                    setTimeout( () => { 
                        this.start_cooldown()
                    }, 250)

                // if ready, do update 
                } else {
                    this.do_update()
                }
            },

            _cooldown() {
                let diff= this.lock_time - Date.now()/1000
                return Math.max(diff, 0)
            },

            get_load_image() {
                function choose(array) {
                    return array[Math.floor(Math.random() * array.length)];
                }
                let choices = [
                    // 앤
                    "https://cdn.discordapp.com/attachments/598883191541071882/677766758454525973/-_-_-2_.gif",
                    // 프레이
                    "https://cdn.discordapp.com/attachments/598883191541071882/677766782173446154/-_-_-2_.gif",
                ]

                return choose(choices)
            }
        },

        computed: {
            start_time() {
                let pad= (x => String(x).padStart(2,0))
                let months= 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
                let ret= ''

                let d= new Date(this.ctx.start)

                let month= pad(months[d.getMonth()])
                let day=   pad(d.getDay())
                let hour=  pad(d.getHours())
                let min=   pad(d.getMinutes())

                return `${month}-${day}, ${hour}:${min}`
            },

            button_text() {
                let cd= Math.ceil(this.cooldown)

                if(cd > 0) {
                    return `Checking thread in ${cd}s...`
                } else if(this.disabled) {
                    return `Waiting for server response...`
                } else {
                    return 'Check thread'
                }
            }
        },

        components: {
            nav_links
        },
    }
</script>

<style scoped>
    #summary {
        margin-bottom: 10px;
    }

    #links {
        text-align: left;
        margin-bottom: 13px;
    }

    #confirmation {
        display: grid;
        text-align: left;
    }

    #confirmed > div {
        line-height: 21px;
    }

    #item_rule {
        margin: 15px 0 20px 0;
    }

    table {
        border-collapse: collapse;
    }

    th, td {
        padding: 10px;
        border: 1px solid #000;
    }

    div.unconfirmed > div {
        color: red;
        line-height: 21px;
        margin: 10px 0 15px 0;
    }

    #button_div > button {
        font-size: 15px;
        padding: 3px 5px 3px 5px;
        margin: 0px 0px 8px 0px;
    }

    td:nth-child(4) > div {
        line-height: 21px;
    }

    tr.losing {
        background-color: rgb(255, 230, 233);
    }

    table.unconfirmed > tbody > tr > td:nth-child(3) {
        color: rgba(0,0,0, 0.35);
    }

    .nav_bar {
        margin-bottom: 21px;
    }
</style>