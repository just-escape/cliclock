<script setup>
import ItemSlot from "@/components/ItemSlot.vue";
import useGameStore from '@/stores/game.js'

const gameStore = useGameStore()
</script>

<template>
<div>
  <div class="row">
    <div class="col">
      <h2>INVENTAIRE</h2>
      {{ gameStore.inventory }}
    </div>
  </div>
  <div class="row">
    <ItemSlot
      v-for="(item, itemIndex) in gameStore.inventory" :key="itemIndex"
      class="col-3" :id="itemIndex"
      :itemId="item ? item.item_id : null"
    />
  </div>
</div>
</template>

<style scoped>
.item-square {
  border: 1px solid transparent;
  box-shadow: inset 0px 0px 20px 25px rgba(0, 0, 0, 0.6);
}
</style>
