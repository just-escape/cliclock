<script setup>
import { BASE_URL } from '@/conf.js'
import axios from 'axios'
import { ref } from 'vue'
import { PLAYER_TEAM, PUZZLE_STATUS } from "@/constants.js"

/* search params */
const name = ref("")
const teamNeutral = ref(true)
const teamBlackthorn = ref(true)
const teamSterling = ref(true)

/* cached results */
const puzzles = ref([])
const items = ref([])
const players = ref([])
const playerPuzzles = ref([])
const playerItems = ref([])

/** */
const playerPuzzlesObsPerPuzzleId = ref({})
const playerPuzzlesUnlPerPuzzleId = ref({})
const playerPuzzlesSolPerPuzzleId = ref({})

/** */
const playerPuzzlesObsPerPlayerId = ref({})
const playerPuzzlesUnlPerPlayerId = ref({})
const playerPuzzlesSolPerPlayerId = ref({})

/** */
const playerItemsPerItemId = ref({})
const playerItemsPerPlayerId = ref({})

/* players */
function orderPlayersById() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => a.id > b.id)
}

function orderPlayersBySlug() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => a.slug > b.slug)
}

function orderPlayersByName() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => a.name > b.name)
}

function orderPlayersByMoney() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => b.money - a.money)
}

function orderPlayersByReputation() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => b.reputation - a.reputation)
}

function orderPlayersBySolvedPuzzles() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => {
        let valueB = (playerPuzzlesSolPerPlayerId.value[b.id] !== undefined ? playerPuzzlesSolPerPlayerId.value[b.id].length : 0)
        let valueA = (playerPuzzlesSolPerPlayerId.value[a.id] !== undefined ? playerPuzzlesSolPerPlayerId.value[a.id].length : 0)
        return valueB - valueA
    })
}

function orderPlayersByNItems() {
    players.value = JSON.parse(JSON.stringify(players.value)).sort((a, b) => {
        let valueB = (playerItemsPerPlayerId.value[b.id] !== undefined ? playerItemsPerPlayerId.value[b.id].length : 0)
        let valueA = (playerItemsPerPlayerId.value[a.id] !== undefined ? playerItemsPerPlayerId.value[a.id].length : 0)
        return valueB - valueA
    })
}

/* puzzles */
function orderPuzzlesById() {
    puzzles.value = JSON.parse(JSON.stringify(puzzles.value)).sort((a, b) => a.id > b.id)
}

function orderPuzzlesBySlug() {
    puzzles.value = JSON.parse(JSON.stringify(puzzles.value)).sort((a, b) => a.slug > b.slug)
}

function orderPuzzlesByName() {
    puzzles.value = JSON.parse(JSON.stringify(puzzles.value)).sort((a, b) => a.name > b.name)
}

function orderPuzzlesByObserved() {
    puzzles.value = JSON.parse(JSON.stringify(puzzles.value)).sort((a, b) => {
        let valueB = (playerPuzzlesObsPerPuzzleId.value[b.id] !== undefined ? playerPuzzlesObsPerPuzzleId.value[b.id].length : 0)
        let valueA = (playerPuzzlesObsPerPuzzleId.value[a.id] !== undefined ? playerPuzzlesObsPerPuzzleId.value[a.id].length : 0)
        return valueB - valueA
    })
}

function orderPuzzlesByUnlocked() {
    puzzles.value = JSON.parse(JSON.stringify(puzzles.value)).sort((a, b) => {
        let valueB = (playerPuzzlesUnlPerPuzzleId.value[b.id] !== undefined ? playerPuzzlesUnlPerPuzzleId.value[b.id].length : 0)
        let valueA = (playerPuzzlesUnlPerPuzzleId.value[a.id] !== undefined ? playerPuzzlesUnlPerPuzzleId.value[a.id].length : 0)
        return valueB - valueA
    })
}

function orderPuzzlesBySolved() {
    puzzles.value = JSON.parse(JSON.stringify(puzzles.value)).sort((a, b) => {
        let valueB = (playerPuzzlesSolPerPuzzleId.value[b.id] !== undefined ? playerPuzzlesSolPerPuzzleId.value[b.id].length : 0)
        let valueA = (playerPuzzlesSolPerPuzzleId.value[a.id] !== undefined ? playerPuzzlesSolPerPuzzleId.value[a.id].length : 0)
        return valueB - valueA
    })
}

/* items */
function orderItemsById() {
    items.value = JSON.parse(JSON.stringify(items.value)).sort((a, b) => a.id > b.id)
}

function orderItemsByName() {
    items.value = JSON.parse(JSON.stringify(items.value)).sort((a, b) => a.name > b.name)
}

function orderItemsByDescription() {
    items.value = JSON.parse(JSON.stringify(items.value)).sort((a, b) => a.description > b.description)
}

function orderItemsByNPlayers() {
    items.value = JSON.parse(JSON.stringify(items.value)).sort((a, b) => {
        let valueB = (playerItemsPerItemId.value[b.id] !== undefined ? playerItemsPerItemId.value[b.id].length : 0)
        let valueA = (playerItemsPerItemId.value[a.id] !== undefined ? playerItemsPerItemId.value[a.id].length : 0)
        return valueB - valueA
    })
}

const url = BASE_URL + '/stats/get_all'
function hit() {
    let teams = []

    if (teamNeutral.value) {
        teams.push(PLAYER_TEAM.NEUTRAL)
    }
    if (teamBlackthorn.value) {
        teams.push(PLAYER_TEAM.BLACKTHORN)
    }
    if (teamSterling.value) {
        teams.push(PLAYER_TEAM.STERLING)
    }

    axios.post(url, {name: name.value, teams: teams}).then(({data}) => {
        puzzles.value = data.puzzles
        items.value = data.items
        players.value = data.players
        playerPuzzles.value = data.player_puzzles
        playerItems.value = data.player_items

        let _playerPuzzlesObsPerPuzzleId = {}
        let _playerPuzzlesUnlPerPuzzleId = {}
        let _playerPuzzlesSolPerPuzzleId = {}
        let _playerPuzzlesObsPerPlayerId = {}
        let _playerPuzzlesUnlPerPlayerId = {}
        let _playerPuzzlesSolPerPlayerId = {}
        for (let pp of playerPuzzles.value) {
            if (_playerPuzzlesObsPerPuzzleId[pp.puzzle_id] === undefined) {
                _playerPuzzlesObsPerPuzzleId[pp.puzzle_id] = []
            }
            if (_playerPuzzlesUnlPerPuzzleId[pp.puzzle_id] === undefined) {
                _playerPuzzlesUnlPerPuzzleId[pp.puzzle_id] = []
            }
            if (_playerPuzzlesSolPerPuzzleId[pp.puzzle_id] === undefined) {
                _playerPuzzlesSolPerPuzzleId[pp.puzzle_id] = []
            }
            if (pp.status == PUZZLE_STATUS.OBSERVED) {
                _playerPuzzlesObsPerPuzzleId[pp.puzzle_id].push(pp.player_id)
            }
            if (pp.status == PUZZLE_STATUS.UNLOCKED) {
                _playerPuzzlesUnlPerPuzzleId[pp.puzzle_id].push(pp.player_id)
            }
            if (pp.status == PUZZLE_STATUS.SOLVED) {
                _playerPuzzlesSolPerPuzzleId[pp.puzzle_id].push(pp.player_id)
            }

            if (_playerPuzzlesObsPerPlayerId[pp.player_id] === undefined) {
                _playerPuzzlesObsPerPlayerId[pp.player_id] = []
            }
            if (_playerPuzzlesUnlPerPlayerId[pp.player_id] === undefined) {
                _playerPuzzlesUnlPerPlayerId[pp.player_id] = []
            }
            if (_playerPuzzlesSolPerPlayerId[pp.player_id] === undefined) {
                _playerPuzzlesSolPerPlayerId[pp.player_id] = []
            }
            if (pp.status == PUZZLE_STATUS.OBSERVED) {
                _playerPuzzlesObsPerPlayerId[pp.player_id].push(pp.puzzle_id)
            }
            if (pp.status == PUZZLE_STATUS.UNLOCKED) {
                _playerPuzzlesUnlPerPlayerId[pp.player_id].push(pp.puzzle_id)
            }
            if (pp.status == PUZZLE_STATUS.SOLVED) {
                _playerPuzzlesSolPerPlayerId[pp.player_id].push(pp.puzzle_id)
            }
        }

        playerPuzzlesObsPerPuzzleId.value = _playerPuzzlesObsPerPuzzleId
        playerPuzzlesUnlPerPuzzleId.value = _playerPuzzlesUnlPerPuzzleId
        playerPuzzlesSolPerPuzzleId.value = _playerPuzzlesSolPerPuzzleId
        playerPuzzlesObsPerPlayerId.value = _playerPuzzlesObsPerPlayerId
        playerPuzzlesUnlPerPlayerId.value = _playerPuzzlesUnlPerPlayerId
        playerPuzzlesSolPerPlayerId.value = _playerPuzzlesSolPerPlayerId

        let _playerItemsPerItemId = {}
        let _playerItemsPerPlayerId = {}
        for (let pi of playerItems.value) {
            if (_playerItemsPerItemId[pi.item_id] === undefined) {
                _playerItemsPerItemId[pi.item_id] = []
            }
            _playerItemsPerItemId[pi.item_id].push(pi.player_id)

            if (_playerItemsPerPlayerId[pi.player_id] === undefined) {
                _playerItemsPerPlayerId[pi.player_id] = []
            }
            _playerItemsPerPlayerId[pi.player_id].push(pi.item_id)
        }

        playerItemsPerItemId.value = _playerItemsPerItemId
        playerItemsPerPlayerId.value = _playerItemsPerPlayerId
    })
}

hit()
</script>

<template>
<div class="container-fluid h-100 w-100 overflow-scroll" style="background: white; color: black">
    <div class="row">
        <div class="col d-flex flex-row">
            <div class="me-4">
                <input type="text" class="form-input" v-model="name"/>
            </div>

            <div class="me-2">
                <input type="checkbox" id="sterling" v-model="teamSterling" />
                <label for="sterling">STERLING</label>
            </div>

            <div class="me-2">
                <input type="checkbox" id="blackthorn" v-model="teamBlackthorn" />
                <label for="blackthorn">BLACKTHORN</label>
            </div>

            <div class="me-5">
                <input type="checkbox" id="neutral" v-model="teamNeutral" />
                <label for="neutral">NEUTRAL</label>
            </div>

            <div>
                <div class="btn btn-primary" @click="hit">Rechercher</div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col">
            <h1>Players</h1>
            <div class="table-responsive">
                <table class="table table-sm table-striped table-hover">
                    <thead>
                        <tr>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersById">Portrait</th>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersBySlug">Slug</th>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersByName">Name</th>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersByMoney">Argent</th>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersByReputation">Réputation</th>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersBySolvedPuzzles">Obs / Déb / Rés</th>
                            <th class="cursor-pointer" scope="col" @click="orderPlayersByNItems">Objets</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                        v-for="player in players" :key="player.id"
                        :class="{
                            'table-danger': player.team == PLAYER_TEAM.BLACKTHORN,
                            'table-primary': player.team == PLAYER_TEAM.STERLING,
                            'text-secondary': player.team == PLAYER_TEAM.NEUTRAL,
                        }"
                        >
                            <td><img :src="BASE_URL + player.avatar" class="img-fluid" style="width: 50px; border-radius: 50%"></td>
                            <td>{{ player.slug }}</td>
                            <td>{{ player.name }}</td>
                            <td>{{ player.money }}</td>
                            <td>{{ player.reputation }}</td>
                            <td>
                                <span v-if="playerPuzzlesObsPerPlayerId[player.id]">
                                    <span class="badge text-bg-secondary">
                                        {{ playerPuzzlesObsPerPlayerId[player.id].length }}
                                    </span>
                                    <span class="badge text-bg-primary">
                                        {{ playerPuzzlesUnlPerPlayerId[player.id].length }}
                                    </span>
                                    <span class="badge text-bg-success">
                                        {{ playerPuzzlesSolPerPlayerId[player.id].length }}
                                    </span>
                                </span>
                                <span v-else>-</span>
                            </td>
                            <td>
                                <span v-if="playerItemsPerPlayerId[player.id]" class="badge text-bg-secondary">
                                    {{ playerItemsPerPlayerId[player.id].length }}
                                </span>
                                <span v-else>-</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col h-100">
            <h1>Énigmes</h1>
            <div class="table-responsive">
                <table class="table table-sm table-striped table-hover">
                    <thead>
                        <tr>
                            <th class="cursor-pointer" scope="col" @click="orderPuzzlesById">Illustration</th>
                            <th class="cursor-pointer" scope="col" @click="orderPuzzlesBySlug">Slug</th>
                            <th class="cursor-pointer" scope="col" @click="orderPuzzlesByName">Name</th>
                            <th class="cursor-pointer" scope="col" @click="orderPuzzlesByObserved">Observé</th>
                            <th class="cursor-pointer" scope="col" @click="orderPuzzlesByUnlocked">Débloqué</th>
                            <th class="cursor-pointer" scope="col" @click="orderPuzzlesBySolved">Résolu</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="puzzle in puzzles" :key="puzzle.id">
                            <td><img :src="BASE_URL + puzzle.picture" class="img-fluid" style="width: 150px"></td>
                            <td>{{ puzzle.slug }}</td>
                            <td>{{ puzzle.name }}</td>
                            <td>
                                <span v-if="playerPuzzlesObsPerPuzzleId[puzzle.id]" class="badge text-bg-secondary">
                                    {{ playerPuzzlesObsPerPuzzleId[puzzle.id].length }}
                                </span>
                                <span v-else>-</span>
                            </td>
                            <td>
                                <span v-if="playerPuzzlesUnlPerPuzzleId[puzzle.id]" class="badge text-bg-secondary">
                                    {{ playerPuzzlesUnlPerPuzzleId[puzzle.id].length }}
                                </span>
                                <span v-else>-</span>
                            </td>
                            <td>
                                <span v-if="playerPuzzlesSolPerPuzzleId[puzzle.id]" class="badge text-bg-secondary">
                                    {{ playerPuzzlesSolPerPuzzleId[puzzle.id].length }}
                                </span>
                                <span v-else>-</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col">
            <h1>Items</h1>
            <div class="table-responsive">
                <table class="table table-sm table-striped table-hover">
                    <thead>
                        <tr>
                            <th class="cursor-pointer" scope="col" @click="orderItemsById">Illustration</th>
                            <th class="cursor-pointer" scope="col" @click="orderItemsByName">Name</th>
                            <th class="cursor-pointer" scope="col" @click="orderItemsByDescription">Description</th>
                            <th class="cursor-pointer" scope="col" @click="orderItemsByNPlayers">Possession</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in items" :key="item.id">
                            <td><img :src="BASE_URL + item.image" class="img-fluid" style="width: 100px"></td>
                            <td>{{ item.name }}</td>
                            <td>{{ item.description }}</td>
                            <td>
                                <span v-if="playerItemsPerItemId[item.id]" class="badge text-bg-secondary">
                                    {{ playerItemsPerItemId[item.id].length }}
                                </span>
                                <span v-else>-</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
</template>

<style scoped></style>