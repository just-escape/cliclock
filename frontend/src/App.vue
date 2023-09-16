<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="container">
    <div class="col">
      <div clas="row">
        <RouterView/>
      </div>
    </div>
    <notifications position="bottom right" :duration="5000"/>
  </div>
</template>

<style scoped>
</style>
