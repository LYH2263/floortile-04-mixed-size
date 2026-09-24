<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import MixedSplitTable from '../components/MixedSplitTable.vue'

const items = ref([])
const detail = ref(null)
const err = ref('')

onMounted(async () => { items.value = (await getJSON('/api/runs')).items })

const isMixed = r => r.result?.kind === 'mixed'
const countOf = r => (isMixed(r) ? r.result.total_count : r.result?.order_count)
const tileLabel = r => (isMixed(r) ? `${r.tile_name} 混铺` : r.tile_name)

async function open(r) {
  err.value = ''
  try {
    detail.value = await getJSON(`/api/runs/${r.id}`)
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <table class="tbl">
      <thead><tr><th>时间</th><th>房间</th><th>砖型</th><th>片数</th></tr></thead>
      <tbody>
        <tr v-for="r in items" :key="r.id" class="clickable" @click="open(r)">
          <td>{{ r.created_at?.slice(0, 19) }}</td>
          <td>{{ r.room_name }}</td>
          <td>{{ tileLabel(r) }}</td>
          <td>{{ countOf(r) }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="err" class="alert">{{ err }}</p>
    <section v-if="detail" class="run-detail">
      <h2>记录 #{{ detail.id }}</h2>
      <p>
        {{ detail.created_at?.slice(0, 19) }} ｜ 房间 {{ detail.room_name }} ｜ 损耗 {{ detail.waste_pct }}%
        <span v-if="detail.note"> ｜ {{ detail.note }}</span>
      </p>
      <MixedSplitTable v-if="detail.result?.kind === 'mixed'" :result="detail.result" />
      <ul v-else>
        <li>砖型 {{ detail.tile_name }}</li>
        <li>净用量 {{ detail.result?.raw_count }} 片，订货 {{ detail.result?.order_count }} 片</li>
      </ul>
      <button @click="detail = null">收起</button>
    </section>
  </div>
</template>
