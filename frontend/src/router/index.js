import { createRouter, createWebHistory } from 'vue-router'
import GameView from '../views/GameView.vue'
import PlayerQrCodesView from '../views/PlayerQrCodesView.vue'
import PuzzleQrCodesView from '../views/PuzzleQrCodesView.vue'
import StatsView from '../views/StatsView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: GameView
    },
    {
      path: '/player_qr_codes/',
      name: 'player_qr_codes',
      component: PlayerQrCodesView,
    },
    {
      path: '/puzzle_qr_codes/',
      name: 'puzzle_qr_codes',
      component: PuzzleQrCodesView,
    },
    {
      path: '/stats/',
      name: 'stats',
      component: StatsView,
    },
  ]
})

export default router
