export { int_to_price }

function int_to_price(val, prescale=1000) {
    val*= prescale
    let unit= 'c'

    if(val > 10*1000*1000) {
        val/= 1000*1000
        unit= 'm'
    } else if(val > 10*1000) {
        val/= 1000
        unit= 'k'
    }

    return `${val}${unit}`
}