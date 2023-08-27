import { defineStore } from 'pinia';
// import main from '@/main.js';


const useWsStore = defineStore({
  id: 'ws',
  state: () => ({
    isConnected: false,
    message: 'test',
    reconnectError: false,
    heartBeatInterval: 20000,
    heartBeatTimer: null,
  }),
  actions: {
    SOCKET_ONOPEN(event) {
      // main.config.globalProperties.$socket = event.currentTarget;
      this.isConnected = true;
      // When the connection is successful, start sending heartbeat messages regularly to avoid being disconnected by the server
      /*this.heartBeatTimer = window.setInterval(() => {
        const message = 'Heartbeat message';
        this.isConnected &&
          main.config.globalProperties.$socket.sendObj({
            code: 200,
            msg: message,
          });
      }, this.heartBeatInterval);*/
    },
    SOCKET_ONCLOSE(event) {
      this.isConnected = false;
      // Stop the heartbeat message when the connection is closed
      window.clearInterval(this.heartBeatTimer);
      this.heartBeatTimer = null;
      console.log('The line is disconnected: ' + new Date());
      console.log(event);
    },
    SOCKET_ONERROR(event) {
      console.error(event);
    },
    SOCKET_ONMESSAGE(message) {
      this.message = message;
      console.info('Message:', message);
    },
    SOCKET_RECONNECT(count) {
      console.info('Message system reconnecting...', count);
    },
    SOCKET_RECONNECT_ERROR() {
      this.reconnectError = true;
    },
  },
});

export default useWsStore
