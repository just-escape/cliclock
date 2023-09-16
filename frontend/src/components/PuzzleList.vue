<script setup>
import { ref, onMounted, watch } from 'vue'
import PuzzleCard from '@/components/PuzzleCard.vue'
import useGameStore from '@/stores/game.js'
import { QrcodeStream } from 'vue-qrcode-reader'
import { Modal } from 'bootstrap'
import { INSTANCE_STATUS } from '@/constants.js'


const gameStore = useGameStore()

watch(() => gameStore.instance, onInstanceUpdate)

function onInstanceUpdate(newValue, oldValue) {
  if (newValue.status != INSTANCE_STATUS.PLAYING && oldValue.status == INSTANCE_STATUS.PLAYING) {
    boostrapModal.hide()
  }
}

let boostrapModal = null
const modal = ref(null)
const pausedCamera = ref(true)
const puzzleSlug = ref("")

function displayPuzzle() {
  gameStore.displayPuzzle(puzzleSlug.value || 'NO_VALUE')
  boostrapModal.hide()
}

function onDetect(detectedQrCodes) {
  gameStore.displayPuzzle(detectedQrCodes[0].rawValue)
  boostrapModal.hide()
}

onMounted(() => {
  boostrapModal = new Modal(modal.value)
  modal.value.addEventListener('hide.bs.modal', () => { pausedCamera.value = true })
  modal.value.addEventListener('show.bs.modal', () => { pausedCamera.value = false })
})
</script>

<template>
<div>
  <div class="row mb-2">
    <div class="col">
      <h2 class="mb-0">JOURNAL</h2>
    </div>
    <div class="col d-flex justify-content-end">
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#observe">
        Observer les lieux <i class="bi-qr-code ps-2"></i>
      </button>
      <div ref="modal" class="modal fade" id="observe" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" style="color: black">Observer</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" style="color: black">
              <QrcodeStream @detect="onDetect" :paused="pausedCamera"></QrcodeStream>
              <input v-model="puzzleSlug" placeholder="code"/>
              <button class="btn btn-primary" @click="displayPuzzle">Observer</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <PuzzleCard v-if="JSON.stringify(gameStore.displayPuzzle) != '{}'"/>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
