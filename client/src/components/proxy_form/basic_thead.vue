<template>
    <thead>
        <tr>
            <th>Item Code</th>
            <th>Item</th>
            <th>Current Bid</th>
            <th><slot></slot></th>
        </tr>
    </thead>
</template>

<script>
    export default {
        props: ["item"]
    }
</script>

th:nth-of-type(2) {
    text-align: left;
}