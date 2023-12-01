<script setup>
import { ref, onMounted, watch, reactive } from 'vue'
import { QrcodeStream } from 'vue-qrcode-reader'
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { Modal } from 'bootstrap'
import useGameStore from '@/stores/game.js'
import { TRADE_STATUS } from "@/constants.js"
import draggable from 'vuedraggable'
import ItemSlot from "@/components/ItemSlot.vue"
import { useNotification } from "@kyvg/vue3-notification"
import empty_slot from "@/assets/empty_slot.png"


const { notify }  = useNotification()
const gameStore = useGameStore()
watch(() => gameStore.trade, onTradeUpdate)

let boostrapModal = null
const modal = ref(null)
const pausedCamera = ref(true)
const localInventory = reactive({data: []})

function onDetect(detectedQrCodes) {
  const detectedValue = detectedQrCodes[0].rawValue
  if (detectedValue.startsWith("player-", "")) {
    gameStore.tradeStart(detectedValue.substring(7))
  } else {
    notify({
      text: "Ce code n'est pas celui d'un joueur.",
      type: "error",
    })
    boostrapModal.hide()
  }
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

function onTradeUpdate(newValue, oldValue) {
  // Make sure the modal is opened, if a trade is initiated by a game master for instance
  if (newValue.trade_id !== null && oldValue.trade_id === null) {
    boostrapModal.show()
    localInventory.data = gameStore.inventory.data
  } else if (newValue.trade_id === null) {
    boostrapModal.hide()
  }
}

function end() {
  gameStore.tradeUpdate()
}

function checkMove(event) {
  if (gameStore.trade.my_status != TRADE_STATUS.TRADING) {
    return false
  }

  if (event.to.classList.contains('to-be-traded')) {
    return gameStore.trade.my_items.length < 3
  }

  return true
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
          <h2 class="modal-title">Échanger</h2>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">

          <div v-if="gameStore.trade.trade_id === null">
            <div class="mb-4 text-center">
              <div>
                Scannez le code d'un autre joueur
              </div>
              <div class="fw-bold">
                OU
              </div>
              <div>
                Laissez ce joueur scanner votre code
              </div>
            </div>
            <div class="d-flex justify-content-center mb-4">
              <vue-qrcode
                :value="'player-' + gameStore.playerSlug"
                :options="{width: 200, margin: 0}"
              />
            </div>
            <div>
              <QrcodeStream @detect="onDetect" :paused="pausedCamera"></QrcodeStream>
            </div>
          </div>

          <div v-else>
            <div
              class="p-2 rounded"
              :class="{accepted: gameStore.trade.peer_status == TRADE_STATUS.ACCEPTED}"
              style="border: 1px solid black"
            >
              <div class="text-center">
                {{ gameStore.trade.peer_name }} <span class="fw-bold">vous donne</span>
              </div>
              <div class="container">
                <div class="row justify-content-end">
                  <div class="col-4" v-if="gameStore.trade.peer_items.length < 3">
                    <img :src="empty_slot" class="img-fluid empty-slot">
                  </div>
                  <div class="col-4" v-if="gameStore.trade.peer_items.length < 2">
                    <img :src="empty_slot" class="img-fluid empty-slot">
                  </div>
                  <div class="col-4" v-if="gameStore.trade.peer_items.length < 1">
                    <img :src="empty_slot" class="img-fluid empty-slot">
                  </div>
                  <ItemSlot
                    v-for="(item, itemIndex) in gameStore.trade.peer_items" :key="itemIndex"
                    class="col-4" :item="item"
                  />
                </div>
              </div>
            </div>

            <hr/>

            <div
              class="p-2 rounded mb-3"
              :class="{accepted: gameStore.trade.my_status == TRADE_STATUS.ACCEPTED}"
              style="border: 1px solid black"
            >
              <div class="text-center">
                <span class="fw-bold">Vous donnez</span> à {{ gameStore.trade.peer_name }}
              </div>
              <div class="position-relative">
                <div class="container">
                  <div class="row justify-content-end">
                    <div class="col-4">
                      <img :src="empty_slot" class="img-fluid empty-slot">
                    </div>
                    <div class="col-4">
                      <img :src="empty_slot" class="img-fluid empty-slot">
                    </div>
                    <div class="col-4">
                      <img :src="empty_slot" class="img-fluid empty-slot">
                    </div>
                  </div>
                </div>

                <div class="container position-absolute top-0 right-0 w-100 h-100">
                  <draggable
                    v-model="gameStore.trade.my_items"
                    handle=".handle"
                    tag="div" class="row justify-content-end to-be-traded h-100"
                    :group="{name: 'trade', pull: 'trade', put: 'trade'}"
                    itemKey="id"
                    :move="checkMove"
                    :sort="false"
                    @end="end"
                  >
                    <template #header>
                      <div v-if="gameStore.trade.my_items.length == 0" class="col"></div>
                    </template>
                    <template #item="{ element }">
                      <ItemSlot class="col-4" :item="element" :draggable="true"/>
                    </template>
                  </draggable>
                </div>
              </div>
          </div>

          <draggable
            v-model="localInventory.data"
            handle=".handle"
            tag="div" class="row trade-inventory"
            :group="{name: 'trade', pull: 'trade', put: 'trade'}"
            itemKey="id"
            :move="checkMove"
            :sort="false"
            @end="end"
          >
            <template #header>
              <div v-if="localInventory.data.length == 0" class="text-center font-italic">
                Votre inventaire est vide
              </div>
            </template>
            <template #item="{ element }">
              <ItemSlot class="col-4" :item="element" :draggable="true" :mb="true"/>
            </template>
          </draggable>

            <div class="d-flex flex-row w-100 justify-content-end">
              <div v-if="gameStore.trade.my_status == TRADE_STATUS.ACCEPTED" class="btn btn-copper" @click="withdraw">Retirer l'offre</div>
              <div v-else class="btn btn-copper" @click="accept">Accepter l'offre</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.accepted {
  background: rgba(61, 255, 61, 0.333);
}

.trade-inventory {
  max-height: 200px;
  overflow: scroll;
}
</style>
