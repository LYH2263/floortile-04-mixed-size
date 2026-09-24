<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import OrderSummary from '../components/OrderSummary.vue'
import TileGridPreview from '../components/TileGridPreview.vue'
import MixedSplitTable from '../components/MixedSplitTable.vue'

const rooms = ref([])
const tiles = ref([])
const roomId = ref(1)
const tileId = ref(1)
const mode = ref('single')
const auxTileId = ref(1)
const mainRatio = ref(60)
const result = ref(null)
const err = ref('')

onMounted(async () => {
  rooms.value = (await getJSON('/api/rooms')).items.filter(r => r.data_quality === 'clean')
  tiles.value = (await getJSON('/api/tiles')).items.filter(t => t.data_quality === 'clean')
  if (rooms.value.length) roomId.value = rooms.value[0].id
  if (tiles.value.length) {
    tileId.value = tiles.value[0].id
    auxTileId.value = tiles.value[1]?.id ?? tiles.value[0].id
  }
})

function switchMode(m) {
  mode.value = m
  result.value = null
  err.value = ''
}

async function preview() {
  err.value = ''
  try {
    if (mode.value === 'mixed') {
      result.value = await getJSON(
        `/api/estimate/mixed?room_id=${roomId.value}&tile_id=${tileId.value}` +
        `&aux_tile_id=${auxTileId.value}&main_ratio_pct=${mainRatio.value}`
      )
    } else {
      result.value = await getJSON(`/api/estimate?room_id=${roomId.value}&tile_id=${tileId.value}`)
    }
  } catch (e) {
    err.value = e.message
    result.value = null
  }
}

async function saveRun() {
  err.value = ''
  try {
    if (mode.value === 'mixed') {
      result.value = await postJSON('/api/estimate/mixed', {
        room_id: roomId.value,
        tile_id: tileId.value,
        aux_tile_id: auxTileId.value,
        main_ratio_pct: Number(mainRatio.value),
        save: true,
        note: '前端保存',
      })
    } else {
      result.value = await postJSON('/api/estimate', {
        room_id: roomId.value,
        tile_id: tileId.value,
        save: true,
        note: '前端保存',
      })
    }
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>下单测算</h1>
    <div class="mode-switch">
      <button :class="{ active: mode === 'single' }" @click="switchMode('single')">单砖</button>
      <button :class="{ active: mode === 'mixed' }" @click="switchMode('mixed')">双砖混铺</button>
    </div>
    <label>房间 <select v-model.number="roomId"><option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option></select></label>
    <template v-if="mode === 'mixed'">
      <label>主砖 <select v-model.number="tileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
      <label>辅砖 <select v-model.number="auxTileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
      <label>主砖面积占比 % <input v-model.number="mainRatio" type="number" min="0" max="100" step="1" /></label>
    </template>
    <label v-else>砖型 <select v-model.number="tileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
    <button @click="preview">试算</button>
    <button @click="saveRun">保存记录</button>
    <p v-if="err" class="alert">{{ err }}</p>
    <template v-if="result?.mode === 'mixed'">
      <MixedSplitTable :result="result" />
      <p v-if="result.run_id" class="saved-hint">已保存为记录 #{{ result.run_id }}</p>
    </template>
    <template v-else>
      <OrderSummary :result="result" />
      <TileGridPreview v-if="result?.layout" :cols="result.layout.cols" :rows="result.layout.rows" :grid-count="result.layout.grid_count" />
    </template>
  </div>
</template>
