<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView/>
  <notifications position="bottom right" :duration="5000"/>
</template>

<style scoped>
</style>
