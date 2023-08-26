import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { BASE_URL } from '@/conf.js'


export const useGameStore = defineStore('game', () => {
  const itemsById = ref({})
  const puzzlesById = ref({})
  const player = ref(null)
  const inventory = ref([])
  const displayedPuzzle = ref(null)
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

  function getPlayerData() {
    const url = BASE_URL + '/get_player_data/a'
    axios
      .get(url)
      .then(({data}) => {
        player.value = data.player
        inventory.value = data.inventory
        displayedPuzzle.value = data.displayed_puzzle
        log.value = data.log
    });
  }

  return { itemsById, puzzlesById, player, inventory, displayedPuzzle, log, getScenarioData, getPlayerData }
})
