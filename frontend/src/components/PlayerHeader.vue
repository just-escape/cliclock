<script setup>
import { BASE_URL } from "@/conf.js"
import useGameStore from '@/stores/game.js'
import { PLAYER_TEAM } from '@/constants.js'


const gameStore = useGameStore()

function getTeamLocale(team) {
  if (team == PLAYER_TEAM.SHERLOCK) {
    return "Holmes"
  } else if (team == PLAYER_TEAM.MORIARTY) {
    return "Moriarty"
  } else if (team == PLAYER_TEAM.NEUTRAL) {
    return "Neutre"
  } else {
    return team
  }
}
</script>

<template>
<div class="jumbotron team-bg">
  <div class="container">
    <div class="row justify-content-end mb-3 py-2 rounded">
      <div v-if="gameStore.player" class="col d-flex flex-row w-100">

        <div class="d-flex flex-column text-end w-100">
          <h2 class="mb-0">{{ gameStore.player.name }}</h2>
          <div>Loyauté : {{ getTeamLocale(gameStore.player.team) }}</div>
        </div>

        <div class="d-flex flex-row align-items-center ms-2">
          <img :src="BASE_URL + gameStore.player.avatar" class="rounded-circle img-fluid" height="175" width="175">
        </div>

      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
