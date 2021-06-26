<template>
    <div>
        [child_2] {{get_status()}}
    </div>
</template>

<script>
    export default {
        inject: ["get_status"],
    }
</script>