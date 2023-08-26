<script setup>
import emptySlot from "@/assets/empty_slot.png"

defineProps({
  id: {
    type: Number,
    required: true,
  },
  item: {
    type: Object,
    required: false,
  },
})
</script>

<template>
<div class="item-square">
  <img :src="item ? item.imgSrc : emptySlot" class="img-fluid w-100 p-3" :data-bs-toggle="item ? 'modal' : ''" :data-bs-target="'#item-' + id">
  <div v-if="item" class="modal fade" :id="'item-' + id" tabindex="-1">
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
