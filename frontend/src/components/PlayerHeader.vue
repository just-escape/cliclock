<script setup>
import { BASE_URL } from "@/conf.js"
import useGameStore from '@/stores/game.js'
import { PLAYER_ROLE, PLAYER_TEAM } from '@/constants.js'


const gameStore = useGameStore()

function getRoleLocale(role) {
  if (role == PLAYER_ROLE.LEADER) {
    return "Leader"
  } else if (role == PLAYER_ROLE.DETECTIVE) {
    return "Détective"
  } else if (role == PLAYER_ROLE.NEGOTIATOR) {
    return "Négociant"
  } else if (role == PLAYER_ROLE.ARTIST) {
    return "Artiste"
  } else {
    return role
  }
}

function getTeamLocale(team) {
  if (team == PLAYER_TEAM.STERLING) {
    return "Sterling"
  } else if (team == PLAYER_TEAM.BLACKTHORN) {
    return "Blackthorn"
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
          <div>Rôle : {{ getRoleLocale(gameStore.player.role) }}</div>
          <div>Loyauté : {{ getTeamLocale(gameStore.player.team) }}</div>
          <div>{{ gameStore.player.money }} <i class="bi-currency-pound"></i></div>
          <div v-if="gameStore.player.reputation !== null">{{ gameStore.player.reputation }} <i class="bi-star-fill"></i></div>
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
