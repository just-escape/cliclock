<script setup>
import { BASE_URL } from "@/conf.js"
import { computed } from 'vue'
import emptySlot from "@/assets/empty_slot.png"
import useGameStore from '../stores/game';

const props = defineProps({
  id: {
    type: Number,
    required: true,
  },
  itemId: {
    type: Number,
    required: false,
  },
})

const gameStore = useGameStore()

const item = computed(() => {
  return props.itemId && gameStore.itemsById[props.itemId] ? gameStore.itemsById[props.itemId] : {}
})
</script>

<template>
<div class="item-square">
  <img
    :src="JSON.stringify(item) != '{}' ? BASE_URL + item.image : emptySlot"
    class="img-fluid w-100 p-3"
    data-bs-toggle="modal"
    :data-bs-target="'#item-' + id"
  >
  <div v-if="JSON.stringify(item) != '{}'" class="modal fade" :id="'item-' + id" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" style="color: black">{{ item.name }}</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" style="color: black">
          {{ item.description }}
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.item-square {
  border: 1px solid transparent;
  box-shadow: inset 0px 0px 20px 25px rgba(0, 0, 0, 0.6);
}
</style>
