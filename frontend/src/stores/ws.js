import { defineStore } from 'pinia'
import useGameStore from '@/stores/game.js'
import uuid4 from "uuid4"


const useWsStore = defineStore({
  id: 'ws',
  state: () => ({
    clientId: uuid4(),
    isConnected: false,
    message: 'test',
    reconnectError: false,
    heartBeatInterval: 20000,
    heartBeatTimer: null,
  }),
  actions: {
    SOCKET_ONOPEN() {
      this.isConnected = true;
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
      useGameStore().onWebsocketEvent(message);
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
