<template>
    <body_row
    :item="item">
        <input 
        type="number" 
        :class="{error, warn}"
        :min="min" 
        :max="max"
        :step="increment"
        @input="bid_submit"
        :value="value"
        /> k
    </body_row>
</template>

<script>
    import body_row from "./basic_body_row.vue"

    export default {
        props: ["item", "increment"],
        inject: ["set_status", "clear_status"],

        data() { return {
            min: this.item.current_bid + this.increment,
            max: 10*1000,
            value: null,

            error: true,
            warn: false,
        }},

        created() {
            // use previous input if available, else set defaults
            this.value= this.item.proxy_bid || this.min
            this.item.proxy_bid= this.value

            this.validate()
        },

        methods: {
            bid_submit(e) {
                let ret= Object.assign({}, this.item)
                ret.proxy_bid= this.value= e.target.value

                if(this.validate())
                    this.$emit("update:item", ret)
            },

            validate() {
                // error if <min
                if(this.value < this.min) {
                    this.set_status(
                        `Your bid for [${this.item.key}] must be at least <b>${this.min}k</b>!`, 
                        this.item.key
                    )
                    this.error= true
                    return false
                } else {
                    this.error= false
                    this.clear_status(this.item.key)
                }

                // warn if >max
                if(this.value > this.max) {
                    this.warn= true
                    this.set_status(
                        `Warning: You are bidding <b>${Number(1000*this.value).toLocaleString()}</b> credits on ${this.item.key}.`,
                        this.item.key,
                        { level: "warn" }
                    )
                } else { 
                    this.warn= false
                    this.clear_status(this.item.key) 
                }
                
                // return
                return true
            },
        },

        components: {
            body_row,
        },
    }
</script>

<style scoped>
    input {
        width: 65px;
        font-size: 15px;
    }

    .error {
        background-color: lightpink;
    }

    .warn {
        background-color: rgb(255, 235, 213);
    }
</style>