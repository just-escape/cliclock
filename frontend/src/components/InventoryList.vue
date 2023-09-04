<script setup>
import ItemSlot from "@/components/ItemSlot.vue"
import useGameStore from '@/stores/game.js'
import draggable from 'vuedraggable'
import { PUZZLE_STATUS } from "@/constants.js"


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
    gameStore.displayedPuzzle &&
    gameStore.displayedPuzzle.status !== PUZZLE_STATUS.OBSERVED
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
  <div class="row">
    <div class="col">
      <h2 class="mb-0">INVENTAIRE</h2>
    </div>
    <div class="col d-flex justify-content-end">
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#trade">
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
    <template #item="{ element }">
      <ItemSlot class="col-3" :item="element"/>
    </template>
  </draggable>
</div>
</template>

<style scoped>
.item-square {
  border: 1px solid transparent;
  box-shadow: inset 0px 0px 20px 25px rgba(0, 0, 0, 0.6);
}
</style>
