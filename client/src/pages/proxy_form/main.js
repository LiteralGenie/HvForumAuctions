import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'


// fetch data
async function load_data() {
    let target= process.env.VUE_APP_SERVER_URL + "/api/proxy/form"
    let data= (await axios.get(target)).data
    
    console.log(target, data)    
    return data
}

// start
async function main() {
    let app= createApp(App)
    app.use(VueAxios, axios)

    // config
    app.config.globalProperties.RESP_DATA= await load_data()
    app.config.globalProperties.DEBUG= process.env.VUE_APP_DEBUG_VIEW
    
    // mount
    app.mount('#app')
}

main()
