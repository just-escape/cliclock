<script setup>
import { ref, onMounted, watch, reactive } from 'vue'
import { QrcodeStream } from 'vue-qrcode-reader'
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { Modal } from 'bootstrap'
import useGameStore from '@/stores/game.js'
import { TRADE_STATUS, INSTANCE_STATUS } from "@/constants.js"
import draggable from 'vuedraggable'
import ItemSlot from "@/components/ItemSlot.vue"


const gameStore = useGameStore()
watch(() => gameStore.trade, onTradeUpdate)

watch(() => gameStore.instance, onInstanceUpdate)

function onInstanceUpdate(newValue, oldValue) {
  if (newValue.status != INSTANCE_STATUS.PLAYING && oldValue.status == INSTANCE_STATUS.PLAYING) {
    boostrapModal.hide()
  }
}

let boostrapModal = null
const modal = ref(null)
const pausedCamera = ref(true)
const localInventory = reactive({data: []})

function onDetect(detectedQrCodes) {
  gameStore.tradeStart(detectedQrCodes[0].rawValue)
}

function testStart() {
  gameStore.tradeStart("menu-jazz")
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

function onMoneyUpdate(event) {
  gameStore.trade.my_money = event.target.value
  gameStore.tradeUpdate()
}

function end() {
  gameStore.tradeUpdate()
}

function checkMove(event) {
  if (gameStore.trade.my_status != TRADE_STATUS.TRADING) {
    return false
  }

  if (event.to.classList.contains('to-be-traded')) {
    return gameStore.trade.my_items.length < 4
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
            <div class="btn btn-primary" @click="testStart">Start</div>
            <div class="d-flex justify-content-center mb-4">
              <vue-qrcode
                :value="gameStore.playerSlug"
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
              <div>
                Argent : {{ gameStore.trade.peer_money }}£
              </div>
              <div>
                Objets :
                <div class="row justify-content-end">
                  <ItemSlot
                    v-for="(item, itemIndex) in gameStore.trade.peer_items" :key="itemIndex"
                    class="col-3" :item="item"
                    :description="false"
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
              <div class="d-flex flex-row align-items-center">
                <div class="me-2">Argent :</div>
                <div class="me-2">
                  <input
                    type="number" min="0" :max="gameStore.player.money" step="1" class="form-control"
                    style="width: 100px"
                    onkeypress="return event.charCode >= 48 && event.charCode <= 57"
                    v-model="gameStore.trade.my_money"
                    :disabled="gameStore.trade.my_status != TRADE_STATUS.TRADING"
                    @input="onMoneyUpdate"
                  >
                </div>
                <div class="font-italic">
                 (Vous avez {{ gameStore.player.money }}£)
                </div>
              </div>
              <div>
                Objets :
                <draggable
                  v-model="gameStore.trade.my_items"
                  tag="div" class="row justify-content-end to-be-traded"
                  :group="{name: 'trade', pull: 'trade', put: 'trade'}"
                  itemKey="id"
                  :move="checkMove"
                  :sort="false"
                  @end="end"
                >
                  <template #header>
                    <!--<ItemSlot style="width: 100px; height: 100px" v-if="gameStore.displayedPuzzleItems.data.length === 0"></ItemSlot>-->
                  </template>
                  <template #item="{ element }">
                    <ItemSlot class="col-3" :item="element" :description="false"/>
                  </template>
                </draggable>
              </div>
          </div>

          <draggable
            v-model="localInventory.data"
            tag="div" class="row"
            :group="{name: 'trade', pull: 'trade', put: 'trade'}"
            itemKey="id"
            :move="checkMove"
            :sort="false"
            @end="end"
          >
            <template #item="{ element }">
              <ItemSlot class="col-3" :item="element" :description="false"/>
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
</style>
