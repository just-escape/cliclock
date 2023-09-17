<script setup>
import PlayerHeader from '@/components/PlayerHeader.vue'
import PuzzleList from '@/components/PuzzleList.vue'
import InventoryList from '@/components/InventoryList.vue'
import SubscriptionForm from '@/components/SubscriptionForm.vue'
import InstanceStatusModal from '@/components/InstanceStatusModal.vue'
import useGameStore from '@/stores/game'
import { PLAYER_ROLE, PLAYER_TEAM } from '@/constants.js'


const gameStore = useGameStore()
</script>

<template>
<SubscriptionForm v-if="!gameStore.playing"/>
<div v-else
  :class="{
    sherlock: gameStore.player.team == PLAYER_TEAM.SHERLOCK,
    moriarty: gameStore.player.team == PLAYER_TEAM.MORIARTY,
    neutral: gameStore.player.team == PLAYER_TEAM.NEUTRAL,
  }"
>
  <PlayerHeader class="mb-2"/>
  <div class="jumbotron">
    <div class="container">
      <PuzzleList
        v-if="gameStore.player.role == PLAYER_ROLE.DETECTIVE || gameStore.player.role == PLAYER_ROLE.NPC"
        class="mb-5"
      />
      <InventoryList/>
      <InstanceStatusModal/>
    </div>
  </div>
</div>
</template>
