<template>
    <tr>
        <td><a @click.stop target="_blank" :href="log.link">{{log.name}}</a></td>
        <td>{{start}}</td>
    </tr>
</template>

<script>
    export default {
        props: ["log"],

        computed: {
            start() {
                let pad= (x => String(x).padStart(2,0))
                let months= 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
                let ret= ''

                let d= new Date(this.log.start*1000)

                let year=  pad(d.getFullYear())
                let month= pad(months[d.getMonth()])
                let day=   pad(d.getDay())
                let hour=  pad(d.getHours())
                let min=   pad(d.getMinutes())

                return `${month}-${day}, ${year}`
            },
        },
    }
</script>

<style scoped>
</style>