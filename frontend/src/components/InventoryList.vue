<script setup>
import cachet from "@/assets/cachet.png"
import gousset from "@/assets/gousset.png"
import letter from "@/assets/letter.png"
import loupe from "@/assets/loupe.png"
import cryptex from "@/assets/cryptex.png"
import ItemSlot from '@/components/ItemSlot.vue'
</script>

<template>
<div>
  <div class="row">
    <div class="col">
      <h2>INVENTAIRE</h2>
    </div>
  </div>
  <div class="row">
    <ItemSlot class="col-3" :id="1" :item="{imgSrc: cachet, name: 'Cachet', description: 'Cet objet a appartenu à Sherlock Holmes lui-même'}"/>
    <ItemSlot class="col-3" :id="2" :item="{imgSrc: gousset, name: 'Montre à gousset', description: 'Cet objet a appartenu à Sherlock Holmes lui-même'}"/>
    <ItemSlot class="col-3" :id="3" :item="{imgSrc: letter, name: 'Lettre mystérieuse', description: 'Cet objet a appartenu à Sherlock Holmes lui-même'}"/>
    <ItemSlot class="col-3" :id="4" :item="{imgSrc: loupe, name: 'Loupe', description: 'Cet objet a appartenu à Sherlock Holmes lui-même'}"/>
    <ItemSlot class="col-3" :id="5" :item="{imgSrc: cryptex, name: 'Cryptex', description: 'Cet objet a appartenu à Sherlock Holmes lui-même'}"/>
    <ItemSlot class="col-3" :id="6"/>
    <ItemSlot class="col-3" :id="7"/>
    <ItemSlot class="col-3" :id="8"/>
    <ItemSlot class="col-3" :id="9"/>
    <ItemSlot class="col-3" :id="10"/>
    <ItemSlot class="col-3" :id="11"/>
    <ItemSlot class="col-3" :id="12"/>
  </div>
</div>
</template>

<style scoped>
.item-square {
  border: 1px solid transparent;
  box-shadow: inset 0px 0px 20px 25px rgba(0, 0, 0, 0.6);
}
</style>
