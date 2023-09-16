<script setup>
import PlayerHeader from '@/components/PlayerHeader.vue'
import PuzzleList from '@/components/PuzzleList.vue'
import InventoryList from '@/components/InventoryList.vue'
import SubscriptionForm from '@/components/SubscriptionForm.vue'
import InstanceStatusModal from '@/components/InstanceStatusModal.vue'
import useGameStore from '@/stores/game'
import { PLAYER_ROLE } from '@/constants.js'


const gameStore = useGameStore()
</script>

<template>
<div v-if="!gameStore.playing">
  <SubscriptionForm/>
</div>
<div v-else>
  <PlayerHeader class="mb-2"/>
  <PuzzleList
    v-if="gameStore.player.role == PLAYER_ROLE.DETECTIVE || gameStore.player.role == PLAYER_ROLE.NPC"
    class="mb-5"
  />
  <InventoryList/>
  <InstanceStatusModal/>
</div>
</template>
