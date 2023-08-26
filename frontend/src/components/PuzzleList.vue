<script setup>
import PuzzleBody from '@/components/PuzzleBody.vue'

let puzzles = [
  {name: "Énigme n°1", description: "<p>hey</p>", pulse: false},
  {name: "Énigme n°2", description: "<p>hey</p>", pulse: false},
  {name: "Énigme n°3", description: "<p>hey</p>", pulse: true},
]
  "<p>À mesure que vous explorez les rues pavées et les salons feutrés de la haute société, les personnages énigmatiques croisent votre chemin. Le sourire sibyllin de la comtesse de Montfort, les murmures inquiétants du vieil antiquaire, les éclats de rire dans le club sélect de gentlemen - chacun cache sa part d'ombre et sa part de vérité.</p>"
  "<p>Alors, brave enquêteur, avec votre esprit aiguisé comme une lame, plongez dans les mystères de cette quête victorienne. Les indices sont dispersés comme des étoiles dans la nuit, attendant d'être reliés pour former une constellation de vérité. À vous de révéler le voile qui dissimule le Cœur d'Écarlate et d'inscrire votre nom dans l'histoire des grands détectives.</p>"
  "<p>Que votre quête soit éclairée par la lueur de la lune et guidée par l'ombre de Sherlock Holmes lui-même.</p>"
</script>

<template>
<div>
  <div class="row">
    <div class="col">
      <h2>JOURNAL</h2>
    </div>
  </div>

  <div class="accordion">
    <div v-for="(puzzle, puzzleIndex) in puzzles" :key="puzzleIndex" class="accordion-item">
      <h2 class="accordion-header">
        <button class="accordion-button collapsed" :class="{pulse: puzzle.pulse}" type="button" data-bs-toggle="collapse" :data-bs-target="'#puzzle-' + puzzleIndex">
          {{ puzzle.name }}
        </button>
      </h2>
      <div :id="'puzzle-' + puzzleIndex" class="accordion-collapse collapse">
        <PuzzleBody class="accordion-body" :description="puzzle.description"/>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% {
    background-color: #feebc0;
  }
  50% {
    background-color: var(--bs-danger);
  }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}

.accordion-button {
  font-weight: bold;
  background: #feebc0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.accordion-button:focus {
  box-shadow: none;
}

.accordion-item {
  border-color: rgba(0, 0, 0, 0.05);
}

.accordion-body {
  background: #feebc0
}
</style>
