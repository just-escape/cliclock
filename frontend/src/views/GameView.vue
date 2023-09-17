<script setup>
import PlayerHeader from '@/components/PlayerHeader.vue'
import PuzzleList from '@/components/PuzzleList.vue'
import InventoryList from '@/components/InventoryList.vue'
import InstanceStatusModal from '@/components/InstanceStatusModal.vue'
import useGameStore from '@/stores/game'
import useWsStore from '@/stores/ws'
import { PLAYER_ROLE, PLAYER_TEAM } from '@/constants.js'
import router from '@/router/index.js'
import { watch } from 'vue'


const gameStore = useGameStore()
const wsStore = useWsStore()
watch(() => gameStore.playerSlugExists, startIfOk)
watch(() => wsStore.isConnected, startIfOk)

let queryString = window.location.search
let urlParams = new URLSearchParams(queryString)

if (urlParams.has('player')) {
  gameStore.playerSlug = urlParams.get('player')
  urlParams.delete('player')
}

router.push({path: '/'})

if (gameStore.playerSlug != "") {
  gameStore.checkPlayerSlugExist()
}

function startIfOk() {
  if (gameStore.playerSlugExists && wsStore.isConnected) {
    gameStore.play()
  }
}
</script>

<template>
<div v-if="!gameStore.playerSlugExists" class="text-center pt-2">
  <div>
    Chargement...
  </div>
  <div class="font-italic">
    (Veuillez vous rapprocher d'un maître du jeu si le chargement est trop long)
  </div>
</div>
<div
  v-else
  :class="{
    sterling: gameStore.player.team == PLAYER_TEAM.STERLING,
    blackthorn: gameStore.player.team == PLAYER_TEAM.BLACKTHORN,
    neutral: gameStore.player.team == PLAYER_TEAM.NEUTRAL,
  }"
>
  <PlayerHeader class="mb-2"/>
  <div class="jumbotron">
    <PuzzleList
      v-if="gameStore.player.role == PLAYER_ROLE.DETECTIVE || gameStore.player.role == PLAYER_ROLE.NPC"
      class="mb-3"
    />
    <InventoryList/>
    <InstanceStatusModal/>
  </div>
</div>
</template>
