<template>
    <div>
        <button 
        id="prev"
        :class="{unavailable: (page_num < 1)}" 
        @click="$emit('update:page_num', --page_num)"
        :disabled="(critical)">
           🠘
        </button>
        
        <span> 
            ({{page_num+1}} of {{num_pages}}) 
        </span>
        
        <button 
        id="next"
        :class="{unavailable: (page_num >= num_pages-1)}"
        @click="$emit('update:page_num', ++page_num)"
        :disabled="next_disabled">
            🠚
        </button>
    </div>
</template>

<script>
    export default {
        props: ["page_num", "num_pages"],
        inject: ["get_status"],

        computed: {
            next_disabled() {
                // check for errors
                let status= this.get_status()

                let error_counts= Object.values(status).map(dct => {
                    let errors= Object.values(dct).filter(x => x.level==="error")
                    return errors.length
                })

                if(error_counts.every(x => x===0))
                    return false

                // get highest page number with errors
                let max_page= error_counts.reduce( (max,count,i) => {
                    return ((count > 0) ? i : max)
                }, null)

                // disable next-button if current page equals max_page
                return this.page_num >= max_page
            },

            critical() {
                let status= this.get_status()

                let flag= Object.values(status).some(dct => {
                    return Object.values(dct).some(info => {
                        return info.level === "critical"  
                    })
                })
                
                return flag
            }
        },
    }
</script>

<style scoped>
    div {
        text-align: center;
        display: flex; justify-content: center;
    }

    div > button {
        text-align: center;
        width: 60px;
        height: 32px;
        font-size: 35px;
        line-height: 0px;
    }

    div > span {
        margin: 0 20px 0 20px;
        font-size: 17px;
        color: rgb(100, 100, 100);
        align-self: center;
    }

    .unavailable {
        visibility: hidden;
    }
</style>