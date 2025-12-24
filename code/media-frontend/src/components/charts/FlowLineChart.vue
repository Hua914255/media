<template>
  <div class="card chart-card">
    <div class="chart-head">
      <div>
        <div class="title">Semantic Flow (ECG)</div>
        <div class="sub">每个 turn 一个点：语义连贯/跳跃波动</div>
      </div>
      <div class="mini">
        <span class="pill">points {{ series.length }}</span>
      </div>
    </div>

    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<script>
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

export default {
  name: 'FlowLineChart',
  components: { VChart },
  props: {
    labels: { type: Array, default: () => [] },
    series: { type: Array, default: () => [] },
  },
  computed: {
    option() {
      return {
        tooltip: { trigger: 'axis' },
        grid: { left: 36, right: 16, top: 26, bottom: 30 },
        xAxis: {
          type: 'category',
          data: this.labels,
          axisLabel: { color: 'rgba(255,255,255,0.65)' },
          axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } },
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 1,
          axisLabel: { color: 'rgba(255,255,255,0.65)' },
          splitLine: { lineStyle: { color: 'rgba(255,255,255,0.10)' } },
        },
        series: [
          {
            name: 'flow',
            type: 'line',
            data: this.series,
            smooth: true,
            showSymbol: false,
            lineStyle: { width: 2 },
            areaStyle: { opacity: 0.12 },
          },
        ],
      }
    },
  },
}
</script>

<style scoped>
.chart-card { height: 100%; display: flex; flex-direction: column; overflow: hidden; }
.chart-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 8px;
}
.title { font-weight: 800; }
.sub { font-size: 12px; opacity: 0.7; margin-top: 2px; }
.chart { flex: 1; min-height: 0; }
.pill {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
}
</style>
