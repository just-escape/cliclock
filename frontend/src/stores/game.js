import { reactive } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { BASE_URL } from '@/conf.js'


const useGameStore = defineStore('game', () => {
  const itemsById = reactive({})
  const puzzlesById = reactive({})
  const player = reactive({})
  const inventory = reactive([])
  const displayedPuzzle = reactive({})
  const log = reactive([])

  function getScenarioData() {
    const url = BASE_URL + '/get_scenario_data/test'
    axios
      .get(url)
      .then(({data}) => {
        Object.assign(itemsById, data.items.reduce(function(obj, x) {
            obj[x.id] = x;
            return obj;
        }, {}))
        Object.assign(puzzlesById, data.puzzles.reduce(function(obj, x) {
            obj[x.id] = x;
            return obj;
        }, {}))
    });
  }

  function getPlayerData() {
    const url = BASE_URL + '/get_player_data/a'
    axios
      .get(url)
      .then(({data}) => {
        Object.assign(player, data.player)
        Object.assign(inventory, data.inventory)
        Object.assign(displayedPuzzle, data.displayed_puzzle)
        Object.assign(log, data.log)
    });
  }

  function onWebsocketEvent(message) {
    if (message.type == "put_player") {
      Object.assign(player, message.data)
    } else if (message.type == "put_inventory") {
      Object.assign(inventory, message.data)
    }
  }

  return {
    itemsById,
    puzzlesById,
    player,
    inventory,
    displayedPuzzle,
    log,
    getScenarioData,
    getPlayerData,
    onWebsocketEvent,
  }
})

export default useGameStore
