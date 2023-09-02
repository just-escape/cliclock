<script setup>
import ItemSlot from '@/components/ItemSlot.vue'
import { computed } from 'vue'
import useGameStore from '../stores/game'

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
</script>

<template>
<div class="card">
  <div class="card-header">
    <div class="font-weight-bold" style="color: black">{{ puzzle.name }}</div>
  </div>

  <div v-html="puzzle.description" class="card-body">
  </div>

  <div class="card-footer">
    <div class="row justify-content-end">
      <ItemSlot class="item-slot-sm" :id="1"/>
      <ItemSlot class="item-slot-sm" :id="2"/>
      <ItemSlot class="item-slot-sm" :id="3"/>
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
