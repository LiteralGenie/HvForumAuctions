<template>
    <tr>
        <td>{{ key }}</td>
        <td v-html="link_elem"/>
        <td>{{ current_bid }}</td>
        <td :class="td_class">
            <slot/>
        </td>
    </tr>
</template>

<script>
    export default {
        props: {
            item: { required: true },

            td_class: { default: "user_input" },
            transforms: { default: {
                current_bid: (x) => (`${x}k`)
            } },
        },

        computed: {
            link_elem() {
                let ret= this.name
                if(this.item.link)
                    ret= `<a @click.stop target="_blank" href="${this.item.link}">${ret}</a>`
                return ret
            },

            name() { return this.transform('name', this.item['name']) },
            key() { return this.transform('key', this.item['key']) },
            current_bid() { return this.transform('current_bid', this.item['current_bid']) },
        },

        methods: {
            transform(key, val) {
                let id= (x => x)
                let fn= this.transforms[key] || id
                return fn(val)
            },
        }
    }
</script>

td:nth-of-type(2) {
    text-align: left;
}