<script setup>
import { ref } from 'vue'
import ItemSlot from '@/components/ItemSlot.vue'
import useGameStore from '../stores/game'
import draggable from 'vuedraggable'
import { PUZZLE_STATUS, PUZZLE_KIND } from "@/constants.js"


const gameStore = useGameStore()

const answer = ref("")

function solvePuzzle() {
  gameStore.checkSolvePuzzle(answer)
}

function del(element) {
  gameStore.displayedPuzzleItems.data = gameStore.displayedPuzzleItems.data.filter(x => x.id != element.id)
  gameStore.checkUnlockPuzzle()
}
</script>

<template>
<div class="card">
  <div class="card-header">
    <div class="font-weight-bold" style="color: black">
      {{ gameStore.displayedPuzzle.name }}<span v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED"> - résolue</span>
    </div>
  </div>

  <div class="card-body d-flex flex-column">
    <div v-html="gameStore.displayedPuzzle.description"></div>
    <div v-if="gameStore.displayedPuzzle.kind == PUZZLE_KIND.KEY_RIDDLE_BOUNTY">
      <draggable
        v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.OBSERVED"
        v-model="gameStore.displayedPuzzleItems.data"
        tag="div" class="row justify-content-end"
        :group="{name: 'items', pull: false, put: true}"
        itemKey="position"
      >
        <template #header>
          <!--<ItemSlot style="width: 100px; height: 100px" v-if="gameStore.displayedPuzzleItems.data.length === 0"></ItemSlot>-->
        </template>
        <template #item="{ element }">
          <ItemSlot class="col-3" :item="element" :description="true" :deletable="true" @delete="() => del(element)"/>
        </template>
      </draggable>
      <div v-else class="row justify-content-end">
        <ItemSlot
          v-for="(item, itemIndex) in gameStore.displayedPuzzle.keys" :key="itemIndex"
          class="col-3" :item="item" :description="true"
        />
      </div>
      <div v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.UNLOCKED">
        <input type="text" v-model="answer">
        <button class="btn btn-primary" @click="solvePuzzle">Répondre</button>
      </div>
    </div>
    <div v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED">
      <div>Vous avez obtenu le butin suivant:</div>
      <div class="row justify-content-end">
        <ItemSlot
          v-for="(item, itemIndex) in gameStore.displayedPuzzle.bounty" :key="itemIndex"
          class="col-3" :item="item" :description="true"
        />
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.item-slot-sm {
  height: 100px;
  width: 100px;
}
</style>
