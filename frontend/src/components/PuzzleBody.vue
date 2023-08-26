<script setup>
import ItemSlot from '@/components/ItemSlot.vue'

defineProps({
  description: {
    type: String,
    required: true,
  },
  items: {
    type: Array,
    required: false,
  },
})
</script>

<template>
<div>
  <div v-html="description"></div>

  <div class="row justify-content-center my-4">
    <hr class="w-75"/>
  </div>

  <div class="row justify-content-end">
    <ItemSlot class="item-slot-sm" :id="1"/>
    <ItemSlot class="item-slot-sm" :id="2"/>
    <ItemSlot class="item-slot-sm" :id="3"/>
  </div>
</div>
</template>

<style scoped>
.item-slot-sm {
  height: 100px;
  width: 100px;
}
</style>
