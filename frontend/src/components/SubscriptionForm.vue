<script setup>
import useGameStore from '../stores/game'
import { QrcodeStream } from 'vue-qrcode-reader'


const gameStore = useGameStore()
gameStore.checkPlayerSlugExist()

function play() {
  gameStore.play()
}

function onInput(event) {
  gameStore.playerSlug = event.target.value
  gameStore.checkPlayerSlugExist()
}

function onDetect(detectedQrCodes) {
  gameStore.playerSlug = detectedQrCodes[0].rawValue
  gameStore.checkPlayerSlugExist()
}
</script>

<template>
<div class="card">
  <div id="parchment"></div>
  <div id="contain">Test</div>
  <div class="card-header">
    <div class="font-weight-bold" style="color: black">
      Inscription
    </div>
  </div>

  <div class="card-body d-flex flex-column">
    <div>Bienvenue</div>
    <QrcodeStream @detect="onDetect"></QrcodeStream>
    <input type="text" :value="gameStore.playerSlug" @input="onInput">

    <div v-if="gameStore.playerSlugExists.exist">
      <div>Hello {{ gameStore.playerSlugExists.name }}</div>
      <button @click="play">Jouer</button>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
