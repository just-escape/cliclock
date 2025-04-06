<script setup>
import { ref } from 'vue'
import ItemSlot from '@/components/ItemSlot.vue'
import useGameStore from '../stores/game'
import draggable from 'vuedraggable'
import { PUZZLE_STATUS, PUZZLE_KIND } from "@/constants.js"
import empty_slot from "@/assets/empty_slot.png"
import i18n from '../locales.js';


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
  <div class="card-header d-flex flex-row justify-content-between align-items-end">
    <div class="font-bold">
      {{ gameStore.displayedPuzzle.name[i18n.global.locale.value] }}
    </div>
    <div v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED">
      {{ $t('solved') }}
      <div class="text-bg-success badge">
        <i class="bi-check" style="font-size: 1.2rem; color: var(--bs-light)"></i>
      </div>
    </div>
    <div v-else-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.UNLOCKED">
      {{ $t('in_progress') }}
      <div class="text-bg-primary badge">
        <i class="bi-exclamation" style="font-size: 1.2rem; color: var(--bs-light)"></i>
      </div>
    </div>
    <div v-else>
      {{ $t('ongoing') }}
      <div class="text-bg-warning badge">
        <i class="bi-lock" style="font-size: 1.2rem; color: var(--bs-light)"></i>
      </div>
    </div>
  </div>

  <div class="card-body d-flex flex-column">
    <img :src="window.env.BASE_URL + gameStore.displayedPuzzle.picture" class="img-fluid w-100">
    <p v-if="gameStore.displayedPuzzle.kind != PUZZLE_KIND.BOUNTY" class="mb-1 mt-2" v-html="gameStore.displayedPuzzle.intro[i18n.global.locale.value]"></p>

    <div v-if="[PUZZLE_KIND.KEY_RIDDLE_BOUNTY, PUZZLE_KIND.KEY_BOUNTY].includes(gameStore.displayedPuzzle.kind)" class="position-relative">
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

      <div v-if="
        [PUZZLE_STATUS.UNLOCKED, PUZZLE_STATUS.SOLVED].includes(gameStore.displayedPuzzle.status) &&
        gameStore.displayedPuzzle.kind == PUZZLE_KIND.KEY_RIDDLE_BOUNTY
      ">
        <p class="mb-1 mt-2" v-html="gameStore.displayedPuzzle.riddle[i18n.global.locale.value]"></p>
        <div class="d-flex flex-row">
          <input :disabled="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED" type="text" class="form-control me-3" v-model="answer">
          <button :disabled="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED" class="btn btn-copper" @click="solvePuzzle">
            {{ $t('answer') }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="gameStore.displayedPuzzle.status == PUZZLE_STATUS.SOLVED">
      <p class="mb-1 mt-2" v-html="gameStore.displayedPuzzle.final[i18n.global.locale.value]"></p>
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
