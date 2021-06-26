<template>
<div>[parent] {{this.get_status('parent')}}</div>
<hr>
<child_1 fn="get_status2"/>
<hr>
<child_2/>
</template>

<script>
import {computed} from "vue"
import child_1 from "./child_1.vue"
import child_2 from "./child_2.vue"

export default {
  data() { return {
    val: "init",
  }},

  created() {
    console.log(this.val)
  },

  methods: {
    get_status: function(src) {
      console.log(this, src)
      return this.val
    },
    
    set_status: function(val) {
      this.val= val
    },
  },

  provide() { return {
    get_status: this.get_status, 
    set_status: this.set_status,
  }},

  components: {
    child_1,
    child_2,
  },
}
</script>
