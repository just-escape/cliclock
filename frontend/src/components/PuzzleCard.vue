<script setup>
import { ref } from 'vue'
import ItemSlot from '@/components/ItemSlot.vue'
import useGameStore from '../stores/game'
import draggable from 'vuedraggable'
import { PUZZLE_STATUS, PUZZLE_KIND } from "@/constants.js"
import { BASE_URL } from "@/conf.js"
import empty_slot from "@/assets/empty_slot.png"


const gameStore = useGameStore()

const answer = ref("")

function solvePuzzle() {
  gameStore.checkSolvePuzzle(answer)
}

function del(element) {
  gameStore.displayedPuzzleItems.data = gameStore.displayedPuzzleItems.data.filter(x => x.id != element.id)
  gameStore.checkUnlockPuzzle()
}
</script>

<template>
<div class="card">
  <!--<div class="card-header">
    <div class="font-weight-bold">
      {{ gameStore.displayedPuzzle.name }}<span v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED"> - résolue</span>
    </div>
  </div>-->

  <div class="card-body d-flex flex-column">
    <div class="position-relative">
      <img :src="BASE_URL + gameStore.displayedPuzzle.picture" class="img-fluid w-100 mb-2">
      <div
        v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED"
        class="position-absolute top-0 right-0 m-2 text-bg-success badge"
      >
        <i class="bi-check-lg" style="font-size: 1.4rem; color: var(--bs-light)"></i>
      </div>
    </div>
  
    <div v-if="gameStore.displayedPuzzle.kind == PUZZLE_KIND.KEY_RIDDLE_BOUNTY" class="position-relative">
      <div class="container" :class="{'mb-2': gameStore.displayedPuzzle.status != PUZZLE_STATUS.OBSERVED }">
        <div class="row justify-content-end">
          <div class="col-4">
            <img :src="empty_slot" class="img-fluid empty-slot">
          </div>
          <div class="col-4" v-if="gameStore.displayedPuzzle.n_keys >= 2">
            <img :src="empty_slot" class="img-fluid empty-slot">
          </div>
          <div class="col-4" v-if="gameStore.displayedPuzzle.n_keys >= 3">
            <img :src="empty_slot" class="img-fluid empty-slot">
          </div>
        </div>
      </div>

      <div
        class="container position-absolute top-0 right-0 w-100"
        :class="{'h-100': gameStore.displayedPuzzle.status == PUZZLE_STATUS.OBSERVED}"
      >
        <draggable
          v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.OBSERVED"
          v-model="gameStore.displayedPuzzleItems.data"
          handle=".handle"
          tag="div" class="row justify-content-end h-100"
          :group="{name: 'items', pull: false, put: true}"
          itemKey="id"
          :sort="false"
        >
          <template #header>
            <div v-if="gameStore.displayedPuzzleItems.data.length == 0" class="col"></div>
          </template>
          <template #item="{ element }">
            <ItemSlot
              class="col-4"
              :item="element"
              :deletable="true"
              @delete="() => del(element)"
            />
          </template>
        </draggable>
        <div v-else class="row justify-content-end">
          <ItemSlot
            v-for="(item, itemIndex) in gameStore.displayedPuzzle.keys" :key="itemIndex"
            class="col-4" :item="item"
          />
        </div>
      </div>

      <div v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.UNLOCKED">
        <p v-html="gameStore.displayedPuzzle.riddle"></p>
        <div class="d-flex flex-row">
          <input type="text" class="form-control me-3" v-model="answer">
          <button class="btn btn-copper" @click="solvePuzzle">Répondre</button>
        </div>
      </div>
    </div>
    <div v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED">
      <div>Vous avez obtenu le butin suivant:</div>
      <div class="container">
        <div class="row justify-content-end">
          <ItemSlot
            v-for="(item, itemIndex) in gameStore.displayedPuzzle.bounty" :key="itemIndex"
            class="col-4" :item="item"
          />
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
