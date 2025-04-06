import "bootstrap/dist/css/bootstrap.min.css"
import 'bootstrap-icons/font/bootstrap-icons.css'
import "bootstrap"
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueNativeSock from "vue-native-websocket-vue3"
import Notifications from '@kyvg/vue3-notification'

import App from './App.vue'
import router from './router/index.js'
import i18n from './locales.js'

const app = createApp(App)

app.use(createPinia())

import useWsStore from "@/stores/ws.js"

const wsStore = useWsStore()

app.use(VueNativeSock, window.env.BASE_URL_WS + "/wss/" + wsStore.clientId, {
  store: wsStore,
  format: 'json',
  reconnection: true,
  reconnectionDelay: 3000,
})

app.use(Notifications)

app.use(i18n)
app.use(router)

app.mount('#app')
