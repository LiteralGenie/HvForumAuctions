<template>
    <form>
        <span class="instructions">Enter your username and desired bid.</span>

        <!-- username input -->
        <div class="username">
            <span class="user_input"><b>Username: </b></span>
            <input 
            ref="start"
            type="text"
            v-model="ctx.user"
            @input="validate()"/>
        </div>

        <!-- bid input table -->
        <table>
            <basic_thead>
                Your bid
            </basic_thead>
            <tbody>
                <bid_row
                v-for="i in filter_selected(ctx)"
                v-model:item="ctx.items[i]"
                :increment="ctx.increment"/>
            </tbody>
        </table>
    </form>
</template>

<script>
    import bid_row from "./bid_input_row.vue"
    import basic_thead from "./basic_thead.vue"

    export default {
        props: ["ctx"],
        inject: ["set_status", "clear_status", "filter_selected"],

        methods: {
            validate(start) {
                let msg= (start ? "" : "Please enter your username.")

                if(!this.ctx.user)
                    this.set_status(msg, "bid_user")
                else
                    this.clear_status("bid_user")
            }
        },

        created() { this.validate(true)  },
        mounted() { this.$refs.start.focus() },
        
        components: {
            bid_row,
            basic_thead,
        },
    }
</script>

<style scoped>
    .username {
        text-align: left;
        margin: 20px 0 20px 0;
    }
</style>