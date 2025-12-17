<template>
  <div class="card chart-card">
    <div class="chart-head">
      <div>
        <div class="title">Compare View</div>
        <div class="sub">散点：flow vs entropy（用于论文/答辩对比）</div>
      </div>
      <div class="mini">
        <span class="pill">pts {{ points.length }}</span>
      </div>
    </div>

    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<script>
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([ScatterChart, GridComponent, TooltipComponent, CanvasRenderer])

export default {
  name: 'CompareScatter',
  components: { VChart },
  props: {
    // points: [{flow, entropy, author, turn}]
    points: { type: Array, default: () => [] },
  },
  computed: {
    option() {
      const human = []
      const ai = []
      for (const p of this.points) {
        const item = [Number(p.flow || 0), Number(p.entropy || 0), p.turn]
        if (p.author === 'human') human.push(item)
        else ai.push(item)
      }
      return {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const [x, y, t] = params.value
            return `T${t}<br/>flow: ${Number(x).toFixed(2)}<br/>entropy: ${Number(y).toFixed(2)}`
          },
        },
        grid: { left: 42, right: 16, top: 26, bottom: 36 },
        xAxis: {
          type: 'value',
          min: 0, max: 1,
          axisLabel: { color: 'rgba(255,255,255,0.65)' },
          splitLine: { lineStyle: { color: 'rgba(255,255,255,0.10)' } },
          name: 'flow',
          nameTextStyle: { color: 'rgba(255,255,255,0.65)' },
        },
        yAxis: {
          type: 'value',
          min: 0, max: 1,
          axisLabel: { color: 'rgba(255,255,255,0.65)' },
          splitLine: { lineStyle: { color: 'rgba(255,255,255,0.10)' } },
          name: 'entropy',
          nameTextStyle: { color: 'rgba(255,255,255,0.65)' },
        },
        series: [
          { name: 'Human', type: 'scatter', data: human, symbolSize: 10, opacity: 0.9 },
          { name: 'AI', type: 'scatter', data: ai, symbolSize: 10, opacity: 0.9 },
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
