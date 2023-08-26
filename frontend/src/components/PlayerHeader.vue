<script setup>
import { BASE_URL } from "@/conf.js"
import { useGameStore } from '@/stores/game.js'

const gameStore = useGameStore()
</script>

<template>
<div>
  <div class="row justify-content-end">
    <div class="col-6 text-end h-100 justify-content-end">
        <div v-if="gameStore.player" class="align-text-bottom">
            <h2 class="mb-0">{{ gameStore.player.name }}</h2>
            <div>{{ gameStore.player.klass }}</div>
            <div>Money: {{ gameStore.player.money }}£</div>
            <div v-if="gameStore.player.reputation !== null">Reputation: {{ gameStore.player.reputation }}</div>
        </div>
    </div>
    <div class="col-2">
        <div class="rounded-circle">
            <img v-if="gameStore.player" :src="BASE_URL + gameStore.player.avatar" class="img-fluid w-100">
        </div>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
