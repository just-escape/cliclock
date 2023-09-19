<script setup>
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { BASE_URL, BASE_URL_UI } from '@/conf.js'
import axios from 'axios'
import { ref } from 'vue'
import { PLAYER_TEAM, PLAYER_ROLE } from "@/constants.js"


const players = ref([])
const SLICE = 12

const url = BASE_URL + '/player/get_all'
axios.get(url).then(({data}) => {
  let slicedPlayers = []
  let playerSlice = []
  let i = 0
  for (let player of data.players) {
    playerSlice.push(JSON.parse(JSON.stringify(player)))
    i = (i + 1) % SLICE
    if (i == 0) {
      slicedPlayers.push(JSON.parse(JSON.stringify(playerSlice)))
      playerSlice = []
    }
  }
  if (i != 0) {
    // Last batch
    slicedPlayers.push(JSON.parse(JSON.stringify(playerSlice)))
  }
  players.value = slicedPlayers
})

function getRoleLabel(role) {
  if (role == PLAYER_ROLE.NPC) {
    return 'PNJ'
  } else if (role == PLAYER_ROLE.LEADER) {
    return 'L'
  } else if (role == PLAYER_ROLE.DETECTIVE) {
    return 'D'
  } else if (role == PLAYER_ROLE.ARTIST) {
    return 'A'
  } else if (role == PLAYER_ROLE.NEGOTIATOR) {
    return 'N'
  } else {
    return '?'
  }
}
</script>

<template>
<div class="container-fluid" size="A4" style="background: white">
    <div v-for="(playerSlice, sliceIndex) in players" :key="sliceIndex" class="row h-100 w-100 pagebreak">
        <div class="d-flex flex-column col-4 mb-3" v-for="player in playerSlice" :key="player.slug">
            <div class="d-flex justify-content-center mt-2">
                <vue-qrcode
                :value="BASE_URL_UI + '?player=' + player.slug"
                :options="{width: 150, margin: 0}"
                />
            </div>
            <div
              class="text-center"
              :class="{
                'text-blackthorn': player.team == PLAYER_TEAM.BLACKTHORN,
                'text-sterling': player.team == PLAYER_TEAM.STERLING,
                'text-neutral': player.team == PLAYER_TEAM.NEUTRAL,
              }"
            >
              {{ player.name }} ({{ getRoleLabel(player.role) }})
            </div>
            <div
              class="text-center"
              :class="{
                'text-blackthorn': player.team == PLAYER_TEAM.BLACKTHORN,
                'text-sterling': player.team == PLAYER_TEAM.STERLING,
                'text-neutral': player.team == PLAYER_TEAM.NEUTRAL,
              }"
            >
              Nom de code : {{ player.slug }}
            </div>
        </div>
    </div>
</div>
</template>

<style scoped>
@media print {
    .pagebreak {
        clear: both;
        page-break-after: always;
    }
}
</style>