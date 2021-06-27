import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'

// debug
const DEBUG_DATA= 0 // {  "increment": 25,  "items": [    {      "cat": "Wep",      "code": "1",      "name": "Legendary Ethereal Shortsword of Slaughter",      "current_bid": 50,      "bidder": "blah",      "link": "https://hentaiverse.org/isekai/equip/50773/41b3481860"    },    {      "cat": "Wep",      "code": "3",      "name": "Legendary Power Helmet of Slaughter",      "current_bid": 0,      "bidder": "",      "link": "https://hentaiverse.org/isekai/equip/50773/41b3481860"    },    {      "cat": "Wep",      "code": "5",      "name": "Legendary Agile Shade Leggings of Negation",      "current_bid": 0,      "bidder": "",      "link": "https://hentaiverse.org/isekai/equip/50773/41b3481860"    },    {      "cat": "Wep",      "code": "7",      "name": "Legenadry Reinforced Leather Gauntlets of the Shadowdancer",      "current_bid": 0,      "bidder": "",      "link": "https://hentaiverse.org/isekai/equip/50773/41b3481860"    },	{      "cat": "Mat",      "code": "72",      "name": "48x Energy Drink",      "current_bid": 0,      "bidder": "",      "link": ""    }  ]}
const DEBUG_VIEW= 1

// helper functions
async function load_data() {
    if(DEBUG_DATA) { 
        return DEBUG_DATA
    } else {
        let resp= await axios.get(process.env.VUE_APP_SERVER_URL + "/proxy_form")
        return resp.data
    }
}

// start
async function main() {
    let app= createApp(App)
    app.use(VueAxios, axios)

    let ctx= await load_data()
    
    app.config.globalProperties.RESP_DATA= ctx
    app.config.globalProperties.DEBUG= DEBUG_VIEW

    app.mount('#app')
}

main()
