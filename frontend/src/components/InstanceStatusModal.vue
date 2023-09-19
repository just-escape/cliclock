<script setup>
import { ref, onMounted, watch } from 'vue'
import useGameStore from '@/stores/game.js'
import { Modal } from 'bootstrap'
import { INSTANCE_STATUS } from '@/constants.js'


let boostrapModal = null
const modal = ref(null)

const gameStore = useGameStore()
watch(() => gameStore.instance, onInstanceUpdate)

function onInstanceUpdate(newValue, oldValue) {
  if (newValue.status != INSTANCE_STATUS.PLAYING && oldValue.status == INSTANCE_STATUS.PLAYING) {
    boostrapModal.show()
  } else if (newValue.status == INSTANCE_STATUS.PLAYING) {
    boostrapModal.hide()
  }
}

onMounted(() => {
  boostrapModal = new Modal(modal.value)
  if (gameStore.instance.status != INSTANCE_STATUS.PLAYING) {
    boostrapModal.show()
  }
})
</script>

<template>
  <div ref="modal" class='modal' :data-bs-backdrop="gameStore.instance.status != INSTANCE_STATUS.PLAYING ? 'static' : false" taxindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1>{{ gameStore.instance.title }}</h1>
        </div>
        <div class="modal-body">
          {{ gameStore.instance.text }}
        </div>
      </div>
    </div>
  </div>
</template>