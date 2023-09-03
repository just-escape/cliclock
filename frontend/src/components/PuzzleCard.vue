<script setup>
import ItemSlot from '@/components/ItemSlot.vue'
import { computed } from 'vue'
import useGameStore from '../stores/game'
import draggable from 'vuedraggable'

const props = defineProps({
  puzzleId: {
    type: Number,
  },
  puzzleStatus: {
    type: String,
  },
})

const gameStore = useGameStore()

const puzzle = computed(() => {
  return props.puzzleId && gameStore.puzzlesById[props.puzzleId] ? gameStore.puzzlesById[props.puzzleId] : {}
})

function end(event) {
  console.log("end here", event)
}
</script>

<template>
<div class="card">
  <div class="card-header">
    <div class="font-weight-bold" style="color: black">{{ puzzle.name }}</div>
  </div>

  <div class="card-body d-flex flex-column">
    <div v-html="puzzle.description"></div>
    <draggable
      v-model="gameStore.displayedPuzzleItems.data"
      tag="div" class="row justify-content-end"
      :group="{name: 'items', pull: false, put: true}"
      itemKey="position"
      @end="end"
    >
      <template #header>
        <div>lala</div>
        <!--<ItemSlot style="width: 100px; height: 100px" v-if="gameStore.displayedPuzzleItems.data.length === 0"></ItemSlot>-->
      </template>
      <template #item="{ element }">
        <ItemSlot class="col-3" :item="element"/>
      </template>
    </draggable>
  </div>
</div>
</template>

<style scoped>
.item-slot-sm {
  height: 100px;
  width: 100px;
}
</style>
