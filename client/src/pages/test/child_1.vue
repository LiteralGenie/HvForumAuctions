<template>
    <div>
        <button
        @click="set_status(Date.now())"
        >
        [child_1] Update val
        </button>
    </div>
</template>

<script>
    export default {
        inject: ["set_status"]
    }
</script>