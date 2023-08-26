<script setup>
import { RouterView } from 'vue-router'
import { useGameStore } from '@/stores/game.js'

const gameStore = useGameStore()
gameStore.getScenarioData()
gameStore.getPlayerData()
</script>

<template>
  <div class="container">
    <div class="col">
      <div clas="row">
        <RouterView/>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
