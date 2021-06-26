export { int_to_price }

function int_to_price(val) {
    let unit= 'k'

    if(val > 1000) {
        val= val / 1000
        unit= 'm'
    }

    return `${val}${unit}`
}