<script setup>
import { BASE_URL } from "@/conf.js"


const props = defineProps({
  item: {
    type: Object,
  },
})
</script>

<template>
<div class="item-square">
  <img
    :src="BASE_URL + props.item.image"
    class="img-fluid w-100 p-3"
    data-bs-toggle="modal"
    :data-bs-target="'#item-' + this.$.uid"
  >
  <div class="modal fade" :id="'item-' + this.$.uid" tabindex="-1">
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
