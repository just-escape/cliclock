import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { BASE_URL } from '@/conf.js'


const useGameStore = defineStore('game', () => {
  const itemsById = ref({})
  const puzzlesById = ref({})
  const player = ref({})
  const inventory = reactive({items: []})
  const displayedPuzzle = ref({})
  const log = ref([])

  function getScenarioData() {
    const url = BASE_URL + '/get_scenario_data/test'
    axios
      .get(url)
      .then(({data}) => {
        itemsById.value = data.items.reduce(function(obj, x) {
            obj[x.id] = x;
            return obj;
        }, {})
        puzzlesById.value = data.puzzles.reduce(function(obj, x) {
            obj[x.id] = x;
            return obj;
        }, {})
    });
  }

  function moveItem(id, newIndex) {
    const url = BASE_URL + '/player/a/move_item'
    axios.get(url, {id: id, new_index: newIndex})
  }

  function displayPuzzle(id) {
    const url = BASE_URL + '/player/a/puzzle/' + id + '/display'
    axios.get(url)
  }

  function getPlayerData() {
    const url = BASE_URL + '/get_player_data/a'
    axios
      .get(url)
      .then(({data}) => {
        player.value = data.player
        inventory.items = [... data.inventory]
        displayedPuzzle.value = data.displayed_puzzle
        log.value = data.log
    });
  }

  function onWebsocketEvent(message) {
    if (message.type == "put_scenario_items") {
      itemsById.value = message.data.reduce(function(obj, x) {
          obj[x.id] = x;
          return obj;
      }, {})
    } else if (message.type == "put_scenario_puzzles") {
      puzzlesById.value = message.data.reduce(function(obj, x) {
          obj[x.id] = x;
          return obj;
      }, {})
    } else if (message.type == "put_player") {
      player.value = message.data
    } else if (message.type == "put_inventory") {
      inventory.items = [... message.data]
    } else if (message.type == "put_displayed_puzzle") {
      displayedPuzzle.value = message.data
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
    moveItem,
    displayPuzzle,
  }
})

export default useGameStore
