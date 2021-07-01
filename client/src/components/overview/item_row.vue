<template>
        <!-- visible row -->
        <tr class="item_row" @click="item_click"
        :class="{hovered}" @mouseover="hovered=1" @mouseout="hovered=0">
            <td>
                <span class="arrow" v-if="!expanded">+</span>
                <span class="arrow" v-if="expanded">-</span>
            </td>
            <td>{{item_key}}</td>
            <td v-html="item_name"/>
            <td><span v-html="winner"/></td>
        </tr>

        <!-- rows hidden until click -->
        <tr v-if="expanded">
            <td colspan="4" class="expanding_td">
                <span class="empty_bid_span"
                v-if="has_no_bids">
                    (no bids yet)
                </span>

                <table class="bid_table"
                v-if="!has_no_bids">
                    <thead>
                        <tr class="bid_header_row">
                            <td>User</td>
                            <td>Bid</td>
                            <td>Time (from start)</td>
                        </tr>
                    </thead>
                    <tbody class="bid_body">
                        <bid_row
                        v-for="(bid,i) in sorted"
                        :bid="sorted[i]"
                        :visible="expanded"
                        :class="{winner: bid.is_winner}"/>
                    </tbody>
                </table>
            </td>
        </tr>
</template>

<script>
    import bid_row from "./bid_row.vue"
    import { int_to_price } from "../../utils/misc_utils.js"

    export default {
        props: ["item"],

        data() { return {
            expanded: false,
            sorted: [],
            hovered: false,
        }},

        created() {
            // inits
            this.sorted= JSON.parse(JSON.stringify(this.item.bids))

            // rescale bids
            this.sorted= this.sorted.map(bid => {
                bid.bid/= process.env.VUE_APP_SCALE_FACTOR
                return bid
            })

            // sort bids by value and time
            this.sorted.sort( (x,y) => {
                let val= (bid => (bid.time))

                if(val(x) < val(y)) {
                    return 1
                } else {
                    return -1
                }
            })
        },

        computed: {
            item_key() {
                return `${this.item.cat}_${this.item.code}`
            },

            item_name() {
                let ret= `${this.item.name}`
                if(this.item.link) {
                    ret= `<a target="_blank" href=${this.item.link}>${ret}</a>`
                }
                return ret
            },

            winner() {
                for(let b of this.item.bids) {
                    if(b.is_winner) {
                        let val= int_to_price(b.bid, 1)
                        return `${val}<br/>(${b.user})`
                    }
                }

                return "(none)"
            },

            has_no_bids() {
                return Boolean(this.sorted.length === 0)
            },
        },

        methods: {
            item_click() {
                this.expanded= !this.expanded
            }
        },

        components: {
            bid_row,
        }
    }
</script>

<style scoped>
    .arrow {
        padding-left: 10px;
        font-size: 30px;
        line-height: 21px;
        margin-right: 10px;
    }

    .item_row > td {
        padding: 10px;
    }

    .bid_header {
        border-top: 1px solid black;
    }

    .item_row {
        border-bottom: 1px solid black;
        border-top: 1px solid #000;
        background-color: rgb(240,240,240);

        cursor: pointer;
    }

    .hovered {
        background-color: rgb(220,220,220);
    }

    .expanding_td {
        padding: 12px 0 12px 0;
    }

    .bid_table {
        height: 100%;
        width: 70%;
        transform: translateX(20%);
        border-collapse: collapse;

        text-align: left;
    }

    .bid_header_row > * {
        font-weight: bold;
        padding-bottom: 5px;
        text-align:
    }

    .bid_table > tbody > tr >>>td {
        padding: 3px;
    }

    .bid_table > tbody > tr >>>td {
        border-top: 1px solid black;
        border-: 1px solid black;
    }
    
    .winner {
        background-color: rgb(232, 255, 214);
        font-weight: bold;
    }
</style>