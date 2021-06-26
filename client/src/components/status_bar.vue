<template>
    <div id="root">
        <div
        class= "error"
        v-for="msg in errors">
            <span v-html="msg"></span>
            <br v-if="msg"/>
        </div>
        
        <div
        class= "warn"
        v-for="msg in warnings">
            <span v-html="msg"></span>
            <br v-if="msg"/>
        </div>
    </div>
</template>

<script>
    import {ref} from 'vue'

    export default {
        props: ["page_num"],
        inject: ["set_status", "get_status"],

        methods: {
            _filter(type) {
                let status= this.get_status()
                return Object.values(status[this.page_num])
                             .filter(x => (x.level === type))
                             .map(x => x.message)
            },
        },

        computed: {
            errors() { return this._filter('error') },
            warnings() { return this._filter('warn') },
        },
    }
</script>


<style>
    :root {
        --warning-color: rgb(217, 121, 20);
        --error-color:   red;
    }
</style>

<style scoped>
    #root {
        margin-top: 20px;
    }

    .warn, .error {
        margin-bottom: 5px;
    }

    .error {
        color: var(--error-color);
    }

    .warn {
        color: var(--warning-color);
    }
</style>