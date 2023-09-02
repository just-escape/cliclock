<script setup>
import ItemSlot from "@/components/ItemSlot.vue"
import useGameStore from '@/stores/game.js'
import draggable from 'vuedraggable'


function end(event) {
  gameStore.moveItem(event.item.id, event.newIndex)
}

const gameStore = useGameStore()
</script>

<template>
<div>
  <div class="row">
    <div class="col">
      <h2>INVENTAIRE</h2>
    </div>
  </div>
  {{ gameStore.inventory.items }}
    <draggable
      v-model="gameStore.inventory.items"
      tag="div" class="row"
      itemKey="position"
      @end="end"
    >
    <template #item="{ element }">
      <ItemSlot
        class="col-3" :id="element.position"
        :itemId="element.item_id"
      />
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
