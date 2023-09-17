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

  if (
    gameStore.displayedPuzzle && (
      gameStore.displayedPuzzle.status !== PUZZLE_STATUS.OBSERVED ||
      gameStore.displayedPuzzleItems.data.length >= 4
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
<div>
  <div class="row mb-2">
    <div class="col d-flex justify-content-between align-items-center">
      <h2 class="mb-0">INVENTAIRE</h2>
      <button class="btn btn-copper" data-bs-toggle="modal" data-bs-target="#trade">
        Échanger <i class="bi-arrow-left-right ps-2"></i>
      </button>
    </div>
  </div>
  <draggable
    v-model="gameStore.inventory.data"
    tag="div" class="row"
    :group="{name: 'items', pull: 'clone', put: false}"
    itemKey="position"
    :move="checkMove"
    @end="end"
  >
    <template #header>
      <div class="text-center font-italic">
        Votre inventaire est vide
      </div>
    </template>
    <template #item="{ element }">
      <ItemSlot class="col-3" :item="element" :description="true"/>
    </template>
  </draggable>
  <TradeModal/>
</div>
</template>

<style scoped>
.item-square {
  border: 1px solid transparent;
  box-shadow: inset 0px 0px 20px 25px rgba(0, 0, 0, 0.6);
}
</style>
