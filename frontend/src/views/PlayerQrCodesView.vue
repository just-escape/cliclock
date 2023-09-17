<script setup>
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { BASE_URL } from '@/conf.js'
import axios from 'axios'
import { ref } from 'vue'
import { PLAYER_TEAM } from "@/constants.js"


const players = ref([])

const url = BASE_URL + '/player/get_all'
axios.get(url).then(({data}) => {
  players.value = data.players
})
</script>

<template>
<div class="container-fluid" size="A4" style="background: white">
    <div class="row h-100 w-100">
        <div class="d-flex flex-column col-4 mb-4" v-for="player in players" :key="player.slug">
            <div class="d-flex justify-content-center">
                <vue-qrcode
                :value="'puzzle-' + player.slug"
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
              {{ player.name }}
            </div>
            <div
              class="text-center"
              :class="{
                'text-blackthorn': player.team == PLAYER_TEAM.BLACKTHORN,
                'text-sterling': player.team == PLAYER_TEAM.STERLING,
                'text-neutral': player.team == PLAYER_TEAM.NEUTRAL,
              }"
            >
              {{ player.slug }}
            </div>
        </div>
    </div>
</div>
</template>

<style scoped>
div[size="A4"] {
  background: white;
  width: 21cm;
  height: 29.7cm;
  display: block;
  margin: 0 auto;
  margin-bottom: 0.5cm;
}

@media print {
  body, div[size="A4"] {
    margin: 0;
    box-shadow: 0;
  }
}

.text-blackthorn {
  color: var(--blackthorn)
}

.text-sterling {
  color: var(--sterling)
}

.text-neutral {
  color: black;
}
</style>