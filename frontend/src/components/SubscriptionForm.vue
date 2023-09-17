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

<div class="container d-flex justify-content-center">
  <div class="row">
    <div class="col">
      <div class="card my-2">
        <div class="card-header text-center">
          <h2>
            Bienvenue
          </h2>
          <div>Veuillez scanner un code de personnage</div>
        </div>

        <div class="card-body d-flex flex-column">
          <div v-if="gameStore.playerSlugExists.exist" class="mb-2 d-flex flex-row justify-content-between align-items-center">
            <div>Personnage : <span class="font-bold">{{ gameStore.playerSlugExists.name }}</span></div>
            <button @click="play" class="btn btn-copper">Commencer</button>
          </div>

          <div class="d-flex flex-column">
            <input v-if="gameStore.allowSlug" class="form-control mb-1" type="text" :value="gameStore.playerSlug" @input="onInput">
            <QrcodeStream @detect="onDetect"></QrcodeStream>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
