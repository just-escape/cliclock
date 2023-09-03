import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { BASE_URL } from '@/conf.js'


const useGameStore = defineStore('game', () => {
  const puzzlesById = ref({})
  const player = ref({})
  const inventory = reactive({data: []})
  const displayedPuzzle = ref({})
  const displayedPuzzleItems = reactive({data: []})

  function getScenarioData() {
    const url = BASE_URL + '/get_scenario_data/test'
    axios
      .get(url)
      .then(({data}) => {
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

  function checkUnlockPuzzle() {
    const url = BASE_URL + '/player/a/puzzle/' + displayPuzzle.value.id + '/unlock'
    axios.get(url, {key_as_player_items: displayedPuzzleItems})
  }

  function getPlayerData() {
    const url = BASE_URL + '/get_player_data/a'
    axios
      .get(url)
      .then(({data}) => {
        player.value = data.player
        displayedPuzzle.value = { puzzle_id: data.displayed_puzzle.puzzle_id, status: "OBSERVED" }
        displayedPuzzleItems.data = []
    });
  }

  function onWebsocketEvent(message) {
    if (message.type == "put_scenario_puzzles") {
      puzzlesById.value = message.data.reduce(function(obj, x) {
          obj[x.id] = x;
          return obj;
      }, {})
    } else if (message.type == "put_player") {
      player.value = message.data
    } else if (message.type == "put_inventory") {
      inventory.data = message.data
    } else if (message.type == "put_displayed_puzzle") {
      displayedPuzzle.value = { puzzle_id: message.data.puzzle_id, status: "OBSERVED" }
      displayedPuzzleItems.data = []
    }
  }

  return {
    puzzlesById,
    player,
    inventory,
    displayedPuzzle,
    displayedPuzzleItems,
    getScenarioData,
    getPlayerData,
    checkUnlockPuzzle,
    onWebsocketEvent,
    moveItem,
    displayPuzzle,
  }
})

export default useGameStore
