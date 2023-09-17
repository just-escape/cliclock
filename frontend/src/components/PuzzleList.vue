<script setup>
import { ref, onMounted, watch } from 'vue'
import PuzzleCard from '@/components/PuzzleCard.vue'
import useGameStore from '@/stores/game.js'
import { QrcodeStream } from 'vue-qrcode-reader'
import { Modal } from 'bootstrap'
import { INSTANCE_STATUS } from '@/constants.js'
import { useNotification } from "@kyvg/vue3-notification"


const gameStore = useGameStore()
const { notify }  = useNotification()

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
  const detectedValue = detectedQrCodes[0].rawValue
  if (detectedValue.startsWith("puzzle-", "")) {
    gameStore.displayPuzzle(detectedValue.substring(7))
  } else {
    notify({
      text: "Ce code ne correspond pas à un lieu du jeu.",
      type: "error",
    })
  }
  boostrapModal.hide()
}

onMounted(() => {
  boostrapModal = new Modal(modal.value)
  modal.value.addEventListener('hide.bs.modal', () => { pausedCamera.value = true })
  modal.value.addEventListener('show.bs.modal', () => { pausedCamera.value = false })
})
</script>

<template>
<div class="container">
  <div class="row mb-2">
    <div class="col d-flex justify-content-between align-items-center">
      <h2 class="mb-0">ENQUÊTE</h2>
      <button class="btn btn-copper" data-bs-toggle="modal" data-bs-target="#observe">
        Observer les lieux <i class="bi-qr-code ps-2"></i>
      </button>
    </div>
    <div ref="modal" class="modal fade" id="observe" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="modal-title">Observer les lieux <i class="bi-qr-code ps-2"></i></h2>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="gameStore.allowSlug" class="d-flex flex-row mb-2">
              <input type="text" v-model="puzzleSlug" class="form-control me-3" placeholder="code"/>
              <button class="btn btn-copper" @click="displayPuzzle">Observer</button>
            </div>

            <QrcodeStream @detect="onDetect" :paused="pausedCamera"></QrcodeStream>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <PuzzleCard v-if="JSON.stringify(gameStore.displayedPuzzle) != '{}'"/>
      <div v-else class="text-center font-italic">Aucune enquête en cours</div>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
