import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'


// fetch data
async function load_data() {
    let params= new URLSearchParams(window.location.search)
    
    let id= params.get('id')
    if(!id) throw TypeError('no id in url params')

    let target= process.env.VUE_APP_SERVER_URL + "/api/logs" + `?id=${id}`
    let data= (await axios.get(target)).data
    
    console.log(target, data)    
    return data
}

// start
async function main() {
    let app= createApp(App)
    app.use(VueAxios, axios)

    // config
    try {
        app.config.globalProperties.RESP_DATA= await load_data()
        app.config.globalProperties.DEBUG= process.env.VUE_APP_DEBUG_VIEW
    } catch(e) {
        console.error(e)
        return
    }
    
    // mount
    app.mount('#app')
}

main()
