<template>
    <div id="root">
        <u><h3>Proxy Bid Form</h3></u>

        <!-- pagination arrows -->
        <advance_bar
        v-model:page_num="page_num"
        :num_pages="NUM_PAGES"/>

        <!-- errors and warnings -->
        <status_bar
        :page_num="page_num"/>        
        <hr>

        <!-- page section -->
        <div id="forms">
            <!-- page 1 (item select) -->
            <div v-if="page_num === 0">
                <item_selection 
                v-model:ctx="ctx"/>
            </div>

            <!-- page 2 (bids / username) -->
            <div v-if="page_num === 1">
                <bid_input 
                v-model:ctx="ctx"/>
            </div>

            <div v-if="page_num === 2">
                <confirm 
                v-model:ctx="ctx"/>
            </div>
        </div>
        <hr>

        <!-- debug -->
        <div id="DEBUG" v-if="DEBUG">
            <pre>
                {{JSON.stringify(status, null, 2)}}
            </pre><br/><pre>
                {{JSON.stringify(ctx, null, 2)}}
            </pre>
        </div>
    </div>
</template>

<script>
    import item_selection from "./item_selection.vue"
    import bid_input from "./bid_input.vue"
    import confirm from "./confirm.vue"
    import advance_bar from "./advance_bar.vue"
    import status_bar from "./status_bar.vue"
    import { computed } from "vue"
    import { int_to_price } from "../../utils/misc_utils.js"

    
    export default {
        name: 'proxy_form',

        data() { return {
            ctx: {},

            NUM_PAGES: 3,
            page_num: 0,

            status: {}
        }},
        
        async created() {            
            // load server data (already fetched)
            this.ctx= this.init_ctx()

            // initialize status container for each page
            ;[...Array(this.NUM_PAGES).keys()].forEach(i => {
                this.status[i]= {}
            })
            
            // add item hashes for convienence
            this.ctx.items.forEach(it => {
                it.key= `${it.cat}_${it.code}`
            });
        },

        // global funcs for errors and warnings
        provide() { return {
            get_status: this.get_status,
            set_status: this.set_status,
            clear_status: this.clear_status,

            filter_selected: this.filter_selected,
            int_to_price,
        }},

        methods: {
            // data initialization
            init_ctx() {
                let ret= JSON.parse(JSON.stringify(this.RESP_DATA))
                let factor= process.env.VUE_APP_SCALE_FACTOR

                // downscale by order of magnitude for convienence
                ret['increment']/= factor
                ret['items'].forEach(dct => {
                    dct['current_bid']/= factor
                })
                
                return ret
            },

            // error and warning funcs
            get_status() {
                return this.status
            },

            set_status(msg, key, {
                level="error"
            }={}) {
                this.status[this.page_num][key]= {
                    message: msg,
                    level,
                }
            },

            clear_status(key) {
                delete this.status[this.page_num][key]
            },

            // global funcs            
            filter_selected(ctx) {
                let ret= []
                ctx.items.forEach( (item,i) => {
                    if(item.selected)
                        ret.push(i)
                })
                return ret
            },
        },
        
        components: {
            item_selection,
            bid_input,
            advance_bar,
            status_bar,
            confirm,
        },
    }
</script>


<style>
    :root {
        --input_highlight: rgba(200,200,200, 0.3);
    }
</style>

<style scoped>
    #forms {
        display: grid;
        justify-content: center;
    }

    >>>.instructions {
        display: block;
        text-align: left;
        margin-bottom: 20px;
        font-size: 105%;
        color: rgb(100,100,100);
    }

    >>>form {
        display: grid;
        width: 800px;
    }

    >>>table {
        border-collapse: collapse;
    }

    >>>th, >>>td {
        padding: 10px;
        border: 1px solid #000;
    }

    h2 {
        margin-bottom: 20px;
    }

    hr:nth-of-type(1) {
        margin: 20px 0 30px 0;
    }
    hr:nth-of-type(2) {
        margin: 40px 0 20px 0;
    }

    >>>.user_input {
        background-color: var(--input_highlight);
    }

    #DEBUG {
        margin-top: 50px;
        text-align: left;
    }
</style>