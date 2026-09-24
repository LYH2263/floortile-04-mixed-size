<script setup>
defineProps({
  result: { type: Object, required: true },
})
</script>
<template>
  <div class="mixed-summary">
    <div class="hero">{{ result.order_count }} 片</div>
    <p>双砖混铺 · 主砖占比 {{ result.main_ratio_pct }}% · 损耗 {{ result.waste_pct }}%</p>
    <table class="tbl split-table">
      <thead>
        <tr><th>分路</th><th>砖型</th><th>占比</th><th>面积 m²</th><th>净片数</th><th>损耗后片数</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>主路</td>
          <td>{{ result.tile?.name ?? `#${result.tile_id}` }}</td>
          <td>{{ result.main_path.ratio_pct }}%</td>
          <td>{{ result.main_path.area_m2 }}</td>
          <td>{{ result.main_path.raw_count }}</td>
          <td>{{ result.main_path.order_count }}</td>
        </tr>
        <tr>
          <td>辅路</td>
          <td>{{ result.aux_tile?.name ?? `#${result.aux_tile_id}` }}</td>
          <td>{{ result.aux_path.ratio_pct }}%</td>
          <td>{{ result.aux_path.area_m2 }}</td>
          <td>{{ result.aux_path.raw_count }}</td>
          <td>{{ result.aux_path.order_count }}</td>
        </tr>
        <tr class="total-row">
          <td>合计</td>
          <td>—</td>
          <td>100%</td>
          <td>{{ result.area_m2 }}</td>
          <td>{{ result.raw_count }}</td>
          <td>{{ result.order_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
