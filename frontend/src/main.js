import "bootstrap/dist/css/bootstrap.min.css"
import 'bootstrap-icons/font/bootstrap-icons.css'
import "bootstrap"
import './assets/main.css'

import { BASE_URL_WS } from "@/conf.js"

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueNativeSock from "vue-native-websocket-vue3"

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())

import useWsStore from "@/stores/ws.js"

const wsStore = useWsStore()

app.use(VueNativeSock, BASE_URL_WS + "/wss/" + wsStore.clientId, {
  store: wsStore,
  format: 'json',
  reconnection: true,
  reconnectionDelay: 3000,
})

app.use(router)

app.mount('#app')
