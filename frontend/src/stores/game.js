import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { BASE_URL, BASE_URL_WS_SUBSCRIBE } from '@/conf.js'
import { useLocalStorage } from "@vueuse/core"
import useWsStore from "@/stores/ws.js"


const useGameStore = defineStore('game', () => {
  const playerSlug = useLocalStorage("playerSlug", "")
  const playerSlugExists = reactive({exist: false, name: ""})
  const playing = ref(false)
  const player = ref({})
  const inventory = reactive({data: []})
  const displayedPuzzle = ref({})
  const displayedPuzzleItems = reactive({data: []})

  const trade = ref({
    trade_id: null,
    my_items: [],
    my_money: 0,
    my_status: null,
    peer_name: "",
    peer_items: [],
    peer_money: 0,
    peer_status: null,
  })

  function tradeStart(peerSlug) {
    const url = BASE_URL + '/trade/start'
    axios.post(url, {peer_slug: peerSlug, my_slug: playerSlug.value})
  }

  function tradeAccept() {
    const url = BASE_URL + '/trade/' + trade.value.trade_id + '/accept'
    axios.post(url, {my_slug: playerSlug.value})
  }

  function tradeWithdraw() {
    const url = BASE_URL + '/trade/' + trade.value.trade_id + '/withdraw'
    axios.post(url, {my_slug: playerSlug.value})
  }

  function tradeUpdate() {
    const url = BASE_URL + '/trade/' + trade.value.trade_id + '/update'
    axios.post(url, {
      my_slug: playerSlug.value,
      my_items: trade.value.my_items,
      my_money: trade.value.my_money,
    })
  }

  function tradeCancel() {
    if (trade.value.trade_id) {
      const url = BASE_URL + '/trade/' + trade.value.trade_id + '/cancel'
      axios.post(url)
    }
  }

  function checkPlayerSlugExist() {
    const url = BASE_URL + '/player/' + (playerSlug.value == "" ? "NO_SLUG" : playerSlug.value) + '/exist'
    axios.get(url).then(({ data }) => {
      playerSlugExists.exist = data.exist
      playerSlugExists.name = data.name
    })
  }

  function moveItem(id, newIndex) {
    const url = BASE_URL + '/player/' + playerSlug.value + '/move_item'
    axios.post(url, {id: id, new_index: newIndex})
  }

  function displayPuzzle(id) {
    const url = BASE_URL + '/player/' + playerSlug.value + '/puzzle/' + id + '/display'
    axios.get(url)
  }

  function checkUnlockPuzzle() {
    const url = BASE_URL + '/player/' + playerSlug.value + '/puzzle/' + displayedPuzzle.value.puzzle_slug + '/unlock'
    axios.post(url, {key_as_player_items: displayedPuzzleItems.data})
  }

  function checkSolvePuzzle(answer) {
    const url = BASE_URL + '/player/' + playerSlug.value + '/puzzle/' + displayedPuzzle.value.puzzle_slug + '/solve'
    axios.post(url, {answer: answer.value})
  }

  function getPlayerData() {
    const url = BASE_URL + '/player/' + playerSlug.value + '/get_data'
    axios.get(url)
  }

  function play() {
    const url = BASE_URL_WS_SUBSCRIBE + '/subscribe'
    axios.post(url, {client_id: useWsStore().clientId, channel: playerSlug.value}).then(
      () => {
        getPlayerData()
        playing.value = true
      }
    )
  }

  function onWebsocketEvent(message) {
    if (message.type == "put_player") {
      player.value = message.data
    } else if (message.type == "put_inventory") {
      inventory.data = message.data
    } else if (message.type == "put_displayed_puzzle") {
      displayedPuzzle.value = message.data
      displayedPuzzleItems.data = []
    } else if (message.type == "put_trade") {
      trade.value = message.data
    }
  }

  return {
    playerSlug,
    playerSlugExists,
    playing,
    player,
    inventory,
    displayedPuzzle,
    displayedPuzzleItems,
    checkPlayerSlugExist,
    getPlayerData,
    checkUnlockPuzzle,
    checkSolvePuzzle,
    onWebsocketEvent,
    moveItem,
    displayPuzzle,
    play,

    trade,
    tradeStart,
    tradeAccept,
    tradeWithdraw,
    tradeUpdate,
    tradeCancel,
  }
})

export default useGameStore
