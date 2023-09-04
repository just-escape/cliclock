<script setup>
import PlayerHeader from '@/components/PlayerHeader.vue'
import PuzzleList from '@/components/PuzzleList.vue'
import InventoryList from '@/components/InventoryList.vue'
import SubscriptionForm from '@/components/SubscriptionForm.vue'
import useGameStore from '@/stores/game'

const gameStore = useGameStore()
</script>

<template>
<div v-if="!gameStore.playing">
  <SubscriptionForm/>
</div>
<div v-else>
  <PlayerHeader class="mb-2"></PlayerHeader>
  <PuzzleList class="mb-5"></PuzzleList>
  <InventoryList></InventoryList>
</div>
</template>
