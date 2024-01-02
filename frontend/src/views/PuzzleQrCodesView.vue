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
<div class="container-fluid" style="background: white">
    <div class="row h-100 w-100">
        <div class="d-flex flex-column col-12 pagebreak" v-for="puzzle in puzzles" :key="puzzle.slug">
            <div class="d-flex justify-content-center mt-5">
                <vue-qrcode
                :value="'puzzle-' + puzzle.slug"
                :options="{width: 500, margin: 0}"
                />
            </div>
            <div class="text-center" style="color: black;font-size: 1.5rem">
                {{ puzzle.name }}
            </div>
        </div>
    </div>
</div>
</template>

<style scoped>
@media print {
    .pagebreak {
        clear: both;
        page-break-after: always;
    }
}
</style>