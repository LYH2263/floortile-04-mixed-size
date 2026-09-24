<script setup>
defineProps({
  // 混铺结果（接口响应或历史 run 的 result 快照），含 main/aux/total_count
  result: { type: Object, required: true },
})
</script>
<template>
  <div class="mixed-split">
    <p>
      房间 {{ result.area_m2 }} m² ｜ 主砖面积占比 {{ result.main_ratio }}% ｜ 损耗 {{ result.waste_pct }}%
    </p>
    <table class="tbl">
      <thead>
        <tr><th>分路</th><th>砖型</th><th>面积 m²</th><th>净片数</th><th>损耗</th><th>订货片数</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>主路</td>
          <td>{{ result.main.tile_name }}</td>
          <td>{{ result.main.area_m2 }}</td>
          <td>{{ result.main.raw_count }}</td>
          <td>{{ result.main.waste_pct }}%</td>
          <td>{{ result.main.order_count }}</td>
        </tr>
        <tr v-if="result.aux">
          <td>辅路</td>
          <td>{{ result.aux.tile_name }}</td>
          <td>{{ result.aux.area_m2 }}</td>
          <td>{{ result.aux.raw_count }}</td>
          <td>{{ result.aux.waste_pct }}%</td>
          <td>{{ result.aux.order_count }}</td>
        </tr>
        <tr class="total-row">
          <td>合计</td>
          <td>—</td>
          <td>{{ result.area_m2 }}</td>
          <td>—</td>
          <td>—</td>
          <td><strong>{{ result.total_count }}</strong></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
