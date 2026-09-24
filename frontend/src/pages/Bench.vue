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
const mode = ref('single') // single | mixed
const mainTileId = ref(1)
const auxTileId = ref(2)
const mainRatio = ref(60)
const result = ref(null)
const mixed = ref(null)
const err = ref('')
const savedMsg = ref('')

onMounted(async () => {
  rooms.value = (await getJSON('/api/rooms')).items.filter(r => r.data_quality === 'clean')
  tiles.value = (await getJSON('/api/tiles')).items.filter(t => t.data_quality === 'clean')
  if (rooms.value.length) roomId.value = rooms.value[0].id
  if (tiles.value.length) {
    tileId.value = tiles.value[0].id
    mainTileId.value = tiles.value[0].id
    auxTileId.value = tiles.value.length > 1 ? tiles.value[1].id : tiles.value[0].id
  }
})

async function preview() {
  err.value = ''
  savedMsg.value = ''
  try {
    if (mode.value === 'mixed') {
      mixed.value = await getJSON(
        `/api/estimate/mixed?room_id=${roomId.value}&main_tile_id=${mainTileId.value}` +
        `&aux_tile_id=${auxTileId.value}&main_ratio=${mainRatio.value}`
      )
      result.value = null
    } else {
      result.value = await getJSON(`/api/estimate?room_id=${roomId.value}&tile_id=${tileId.value}`)
      mixed.value = null
    }
  } catch (e) {
    err.value = e.message
    result.value = null
    mixed.value = null
  }
}

async function saveRun() {
  err.value = ''
  savedMsg.value = ''
  try {
    if (mode.value === 'mixed') {
      mixed.value = await postJSON('/api/estimate/mixed', {
        room_id: roomId.value,
        main_tile_id: mainTileId.value,
        aux_tile_id: auxTileId.value,
        main_ratio: Number(mainRatio.value),
        save: true,
        note: '前端保存',
      })
      savedMsg.value = `已保存 #${mixed.value.run_id}`
    } else {
      result.value = await postJSON('/api/estimate', {
        room_id: roomId.value,
        tile_id: tileId.value,
        save: true,
        note: '前端保存',
      })
      savedMsg.value = `已保存 #${result.value.run_id}`
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
      <label><input type="radio" value="single" v-model="mode" /> 单砖</label>
      <label><input type="radio" value="mixed" v-model="mode" /> 双砖混铺</label>
    </div>
    <label>房间 <select v-model.number="roomId"><option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option></select></label>
    <template v-if="mode === 'single'">
      <label>砖型 <select v-model.number="tileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
    </template>
    <template v-else>
      <label>主砖 <select v-model.number="mainTileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
      <label>辅砖 <select v-model.number="auxTileId"><option v-for="t in tiles" :key="t.id" :value="t.id">{{ t.name }}</option></select></label>
      <label>主砖面积占比（%）<input type="number" min="1" max="100" step="1" v-model.number="mainRatio" /></label>
    </template>
    <button @click="preview">试算</button>
    <button @click="saveRun">保存记录</button>
    <span v-if="savedMsg" class="ok">{{ savedMsg }}</span>
    <p v-if="err" class="alert">{{ err }}</p>
    <template v-if="mode === 'single'">
      <OrderSummary :result="result" />
      <TileGridPreview v-if="result?.layout" :cols="result.layout.cols" :rows="result.layout.rows" :grid-count="result.layout.grid_count" />
    </template>
    <MixedSplitTable v-else-if="mixed" :result="mixed" />
  </div>
</template>
