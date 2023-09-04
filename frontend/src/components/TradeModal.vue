<script setup>
import { ref, onMounted } from 'vue'
import { QrcodeStream } from 'vue-qrcode-reader'
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { Modal } from 'bootstrap'


let boostrapModal = null
const modal = ref(null)
const pausedCamera = ref(true)

function onDetect(detectedQrCodes) {
  console.log(detectedQrCodes[0].rawValue)
  // gameStore.displayPuzzle(detectedQrCodes[0].rawValue)
}

onMounted(() => {
  boostrapModal = new Modal(modal.value)
  modal.value.addEventListener('hide.bs.modal', () => { pausedCamera.value = true })
  modal.value.addEventListener('show.bs.modal', () => { pausedCamera.value = false })
})
</script>

<template>
  <div ref="modal" class="modal fade" id="trade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" style="color: black">Échanger</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" style="color: black">
          <div class="mb-4 text-center">
            <div>
              Veuillez scanner un QR code d'échange d'un autre joueur
            </div>
            <div class="fw-bold">
              OU
            </div>
            <div>
              Laissez ce joueur scanner votre QR code d'échange
            </div>
          </div>
          <div class="d-flex justify-content-center mb-4">
            <vue-qrcode
              :value="hello"
              :options="{width: 300, margin: 0}"
            />
          </div>
          <div>
            <QrcodeStream @detect="onDetect" :paused="pausedCamera"></QrcodeStream>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
