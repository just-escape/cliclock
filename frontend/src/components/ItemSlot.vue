<script setup>
import { ref, getCurrentInstance } from 'vue'
import { BASE_URL } from "@/conf.js"

const instance = getCurrentInstance()
const uuid = ref(instance.uid)

const props = defineProps({
  item: {
    type: Object,
  },
  deletable: {
    type: Boolean,
    default: false,
  },
  description: {
    type: Boolean,
  }
})
</script>

<template>
<div class="item-square position-relative">
  <button v-if="deletable" @click="$emit('delete')" class="position-absolute btn btn-transparent" style="top: 0; right: 0">
    <i class="bi-x-square-fill"></i>
  </button>
  <img
    :src="BASE_URL + props.item.image"
    class="img-fluid w-100 p-3"
    :data-bs-toggle="description ? 'modal' : null"
    :data-bs-target="description ? '#item-' + uuid : null"
  >
  <div v-if="description" class="modal fade" :id="'item-' + uuid" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" style="color: black">{{ props.item.name }}</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" style="color: black">
          {{ props.item.description }}
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
