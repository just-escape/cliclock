<script setup>
import { BASE_URL } from "@/conf.js"
import useGameStore from '@/stores/game.js'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n({
  inheritLocale: true,
  useScope: 'global'
})

function setLocale(newLocale) {
  locale.value = newLocale;
}

const gameStore = useGameStore()
</script>

<template>
<div class="jumbotron team-bg">
  <div class="container">
    <div class="flex-row d-flex justify-content-between mb-3 py-2 rounded">
      <div>
        <i class="bi bi-translate me-2" style="font-size: 1.5rem; color: #bbbbbb"></i>
        <div class="btn btn-outline-secondary me-2" style="color: #bbbbbb; border-color: #bbbbbb" @click="setLocale('fr')">FR</div>
        <div class="btn btn-outline-secondary" style="color: #bbbbbb; border-color: #bbbbbb" @click="setLocale('en')">EN</div>
      </div>
      <div>
        <div v-if="gameStore.player" class="col d-flex flex-row w-100">

          <div class="d-flex flex-column text-end w-100">
            <h2 class="mb-0">{{ gameStore.player.name }}</h2>
            <!-- || '' while it loads -->
            <div>{{ $t('loyalty') }}{{ $t(gameStore.player.team || '') }}</div>
          </div>

          <div class="d-flex flex-row align-items-center ms-2">
            <img :src="BASE_URL + gameStore.player.avatar" class="rounded-circle img-fluid" height="175" width="175">
          </div>

        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
</style>
