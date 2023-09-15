<script setup>
import { ref, onMounted, watch } from 'vue'
import { QrcodeStream } from 'vue-qrcode-reader'
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { Modal } from 'bootstrap'
import useGameStore from '@/stores/game.js'
import { TRADE_STATUS } from "@/constants.js"


const gameStore = useGameStore()
watch(() => gameStore.trade, onTradeUpdate)

let boostrapModal = null
const modal = ref(null)
const pausedCamera = ref(true)

function onDetect(detectedQrCodes) {
  gameStore.tradeStart(detectedQrCodes[0].rawValue)
}

function testStart() {
  gameStore.tradeStart("k")
}

function accept() {
  gameStore.tradeAccept()
}

function withdraw() {
  gameStore.tradeWithdraw()
}

function onModalHide() {
  pausedCamera.value = true
  gameStore.tradeCancel()
}

function onTradeUpdate() {
  // Make sure the modal is opened, if a trade is initiated by a game master for instance
  if (gameStore.trade.trade_id !== null) {
    boostrapModal.show()
  } else {
    boostrapModal.hide()
  }
}

function onMoneyUpdate(event) {
  gameStore.trade.my_money = event.target.value
  gameStore.tradeUpdate()
}

onMounted(() => {
  boostrapModal = new Modal(modal.value)
  modal.value.addEventListener('hide.bs.modal', onModalHide)
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

          <div v-if="gameStore.trade.trade_id === null">
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
            <div class="btn btn-primary" @click="testStart">Start</div>
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

          <div v-else>

            <div>
              <div class="text-center">
                Offert par {{ gameStore.trade.peer_name }}
              </div>
              <div>
                Argent: {{ gameStore.trade.peer_money }}£
              </div>
              <div>
                Items: {{ gameStore.trade.peer_items }}
              </div>
              <div v-if="gameStore.trade.peer_status == TRADE_STATUS.ACCEPTED">
                VALIDÉ
              </div>
            </div>
            
            <hr/>

            <div>
              <div class="text-center">
                Offert par vous
              </div>
              <div class="row">
                <div class="col-auto">Argent:</div>
                <div class="col-auto">
                  <input
                    type="number" min="0" :max="gameStore.player.money" step="1" class="form-control"
                    onkeypress="return event.charCode >= 48 && event.charCode <= 57"
                    v-model="gameStore.trade.my_money"
                    @input="onMoneyUpdate"
                  >
                </div>
                <div class="col-auto">
                 (Vous avez {{ gameStore.player.money }}£)
                </div>
              </div>
              <div>
                Items: {{ gameStore.trade.my_items }}
              </div>
              <div v-if="gameStore.trade.my_status == TRADE_STATUS.ACCEPTED">
                VALIDÉ
              </div>

              <div v-if="gameStore.trade.my_status == TRADE_STATUS.ACCEPTED" class="btn btn-primary" @click="withdraw">Withdraw</div>
              <div v-else class="btn btn-primary" @click="accept">Accept</div>
            </div>

          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
