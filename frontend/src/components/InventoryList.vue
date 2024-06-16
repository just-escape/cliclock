<script setup>
import ItemSlot from "@/components/ItemSlot.vue"
import useGameStore from '@/stores/game.js'
import draggable from 'vuedraggable'
import { PUZZLE_STATUS } from "@/constants.js"
import TradeModal from "@/components/TradeModal.vue"


function end(event) {
  if (event.from === event.to) {
    if (event.oldIndex != event.newIndex) {
      gameStore.moveItem(gameStore.inventory.data[event.newIndex].id, event.newIndex)
    }
  } else {
    gameStore.checkUnlockPuzzle()
  }
}

function checkMove(event) {
  if (event.from === event.to) {
    return true
  }

  console.log(gameStore.displayedPuzzleItems.data.length, gameStore.displayedPuzzle.n_keys, gameStore.displayedPuzzleItems.data.length >= gameStore.displayedPuzzle.n_keys)
  if (
    gameStore.displayedPuzzle && (
      gameStore.displayedPuzzle.status !== PUZZLE_STATUS.OBSERVED ||
      gameStore.displayedPuzzleItems.data.length >= gameStore.displayedPuzzle.n_keys
    )
  ) {
    return false
  }

  // Prevent duplication in the puzzle inventory
  return !gameStore.displayedPuzzleItems.data.map(item => item.id).includes(event.draggedContext.element.id)
}

const gameStore = useGameStore()
</script>

<template>
<div class="container">
  <div class="row mb-2">
    <div class="col d-flex justify-content-between align-items-center">
      <h2 class="mb-0">{{ $t('inventory') }}</h2>
      <button class="btn btn-copper" data-bs-toggle="modal" data-bs-target="#trade">
        {{ $t('trade') }} <i class="bi-arrow-left-right ps-2"></i>
      </button>
    </div>
  </div>
  <draggable
    v-model="gameStore.inventory.data"
    handle=".handle"
    tag="div" class="row inventory"
    :group="{name: 'items', pull: 'clone', put: false}"
    itemKey="id"
    :move="checkMove"
    @end="end"
  >
    <template #header>
      <div v-if="gameStore.inventory.data.length == 0" class="text-center font-italic">
        {{ $t('empty_inventory') }}
      </div>
    </template>
    <template #item="{ element }">
      <ItemSlot class="col-4" :item="element" :description="true" :draggable="true" :mb="true"/>
    </template>
  </draggable>
  <TradeModal/>
</div>
</template>

<style scoped>
.inventory {
  max-height: 275px;
  overflow: scroll;
}
</style>
