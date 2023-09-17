<script setup>
import VueQrcode from '@chenfengyuan/vue-qrcode'
import { BASE_URL } from '@/conf.js'
import axios from 'axios'
import { ref } from 'vue'


const puzzles = ref([])

const url = BASE_URL + '/puzzle/get_all'
axios.get(url).then(({data}) => {
  puzzles.value = data.puzzles
})
</script>

<template>
<div class="container-fluid" size="A4" style="background: white">
    <div class="row h-100 w-100">
        <div class="d-flex flex-column col-4 mb-4" v-for="puzzle in puzzles" :key="puzzle.slug">
            <div class="d-flex justify-content-center">
                <vue-qrcode
                :value="'puzzle-' + puzzle.slug"
                :options="{width: 150, margin: 0}"
                />
            </div>
            <div class="text-center" style="color: black">
                {{ puzzle.slug }}
            </div>
        </div>
    </div>
</div>
</template>

<style scoped>
div[size="A4"] {
  background: white;
  width: 21cm;
  height: 29.7cm;
  display: block;
  margin: 0 auto;
  margin-bottom: 0.5cm;
}

@media print {
  body, div[size="A4"] {
    margin: 0;
    box-shadow: 0;
  }
}
</style>