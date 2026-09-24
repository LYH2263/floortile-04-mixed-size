<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const tileNames = ref({})
const openId = ref(null)

onMounted(async () => {
  items.value = (await getJSON('/api/runs')).items
  const tiles = (await getJSON('/api/tiles')).items
  tileNames.value = Object.fromEntries(tiles.map(t => [t.id, t.name]))
})

function toggle(id) {
  openId.value = openId.value === id ? null : id
}

function tileName(r, id) {
  return tileNames.value[id] ?? (id === r.tile_id ? r.tile_name : `#${id}`)
}
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <table class="tbl">
      <thead><tr><th>时间</th><th>房间</th><th>砖型</th><th>片数</th><th></th></tr></thead>
      <tbody>
        <template v-for="r in items" :key="r.id">
          <tr @click="toggle(r.id)" class="run-row">
            <td>{{ r.created_at?.slice(0, 19) }}</td>
            <td>{{ r.room_name }}</td>
            <td>
              {{ r.tile_name }}
              <span v-if="r.result?.mode === 'mixed'" class="tag">混铺</span>
            </td>
            <td>{{ r.result?.order_count }}</td>
            <td>{{ openId === r.id ? '▾' : '▸' }}</td>
          </tr>
          <tr v-if="openId === r.id" class="detail-row">
            <td colspan="5">
              <template v-if="r.result?.mode === 'mixed'">
                <p>双砖混铺 · 损耗 {{ r.waste_pct }}%（保存时快照，不随默认损耗重算）</p>
                <table class="tbl split-table">
                  <thead>
                    <tr><th>分路</th><th>砖型</th><th>占比</th><th>面积 m²</th><th>净片数</th><th>损耗后片数</th></tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>主路</td>
                      <td>{{ tileName(r, r.result.tile_id) }}</td>
                      <td>{{ r.result.main_path.ratio_pct }}%</td>
                      <td>{{ r.result.main_path.area_m2 }}</td>
                      <td>{{ r.result.main_path.raw_count }}</td>
                      <td>{{ r.result.main_path.order_count }}</td>
                    </tr>
                    <tr>
                      <td>辅路</td>
                      <td>{{ tileName(r, r.result.aux_tile_id) }}</td>
                      <td>{{ r.result.aux_path.ratio_pct }}%</td>
                      <td>{{ r.result.aux_path.area_m2 }}</td>
                      <td>{{ r.result.aux_path.raw_count }}</td>
                      <td>{{ r.result.aux_path.order_count }}</td>
                    </tr>
                    <tr class="total-row">
                      <td>合计</td>
                      <td>—</td>
                      <td>100%</td>
                      <td>{{ r.result.area_m2 }}</td>
                      <td>{{ r.result.raw_count }}</td>
                      <td>{{ r.result.order_count }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <template v-else>
                <p>
                  单砖 · 净用量 {{ r.result?.raw_count }} 片 · 损耗 {{ r.waste_pct }}% ·
                  地面 {{ r.result?.area_m2 }} m² · 单砖 {{ r.result?.piece_m2 }} m²
                </p>
              </template>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
