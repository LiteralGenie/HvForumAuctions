<template>
    <form>
        <span class="instructions">Select the items you want to bid on.</span>
        <table>
            <basic_thead/>
            <tbody>
                <item_row 
                v-for="(it,i) in ctx.items"
                v-model:item="ctx.items[i]"
                />
            </tbody>
        </table>
    </form>
</template>

<script>
    import item_row from "./item_selection_row.vue"
    import basic_thead from "./basic_thead.vue"

    export default {
        name: 'proxy_form_1',
        
        inject: ["set_status", "clear_status"],
        props: ["ctx"],

        methods: {
            validate(ctx, start) {
                let msg= (start ? "" : "Please select at least one item")

                if (ctx.items.some(x => {
                    if(x.selected === true) {
                        this.clear_status("no_items_selected")
                        return true
                    }
                })) { return true }
                
                this.set_status(msg, "no_items_selected")
                return false
            }
        },

        watch: {
            ctx: {
                deep: true,
                handler(_, new_ctx) {
                    this.validate(new_ctx)
                }
            }
        },

        created() { this.validate(this.ctx, true) },
        
        components: {
            item_row,
            basic_thead
        },
    }
</script>

<style scoped>
    .selected {
        background-color: rgba(187, 212, 235, 0.9);
    }
</style>