<script setup>
import { ref, getCurrentInstance } from 'vue'
import { BASE_URL } from "@/conf.js"
import grab_hand from "@/assets/grab-hand.svg"
import eye from "@/assets/eye.svg"
import x from "@/assets/x.svg"


const instance = getCurrentInstance()
const uuid = ref(instance.uid)

const props = defineProps({
  item: {
    type: Object,
  },
  draggable: {
    type: Boolean,
    default: false,
  },
  deletable: {
    type: Boolean,
    default: false,
  },
  description: {
    type: Boolean,
  },
  mb: {
    type: Boolean,
    default: false,
  }
})
</script>

<template>
<div class="position-relative">
  <!-- Toolbar -->
  <div class="d-flex flex-row position-absolute top-0 right-075-rem">
    <div v-if="draggable" class="toolbox-item handle">
      <img :src="grab_hand">
    </div>
    <div
      v-if="description" class="toolbox-item"
      :data-bs-toggle="description ? 'modal' : null"
      :data-bs-target="description ? '#item-' + uuid : null"
    >
      <img :src="eye">
    </div>
    <div v-if="deletable" class="toolbox-item" @click="$emit('delete')">
      <img :src="x" class="sm">
    </div>
  </div>

  <img
    :src="BASE_URL + props.item.image"
    class="img-fluid w-100 item-square"
    :class="{'mb-3': mb}"
  >

  <div v-if="description" class="modal fade" :id="'item-' + uuid" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <!--<h2 class="modal-title">{{ props.item.name }}</h2>-->
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          {{ props.item.description }}
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.toolbox-item {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(180deg, #8b725c 0%, #9f8b6e 19%, #d9cca5 51%, #9f8b6e 100%);
  border-radius: 0.25rem;
  border: 1px solid black;
  color: var(--bs-light);
}

.toolbox-item:hover {
  cursor: pointer;
}

.toolbox-item img {
  width: 23px;
}

.toolbox-item img.sm {
  width: 18px;
}
</style>
