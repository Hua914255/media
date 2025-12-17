<template>
  <div class="card chart-card">
    <div class="chart-head">
      <div>
        <div class="title">Creative Entropy</div>
        <div class="sub">实时仪表盘：越高越“出乎意料”</div>
      </div>
      <div class="mini">
        <span class="pill">now {{ value.toFixed(2) }}</span>
      </div>
    </div>

    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<script>
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { GaugeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([GaugeChart, TooltipComponent, CanvasRenderer])

export default {
  name: 'EntropyGauge',
  components: { VChart },
  props: {
    value: { type: Number, default: 0 },
  },
  computed: {
    option() {
      const v = Math.max(0, Math.min(1, Number(this.value || 0))) * 100
      return {
        tooltip: { formatter: '{a}<br/>{b}: {c}%' },
        series: [
          {
            name: 'entropy',
            type: 'gauge',
            startAngle: 200,
            endAngle: -20,
            min: 0,
            max: 100,
            splitNumber: 5,
            progress: { show: true, width: 12 },
            axisLine: { lineStyle: { width: 12, opacity: 0.35 } },
            axisTick: { distance: -18, length: 6, lineStyle: { opacity: 0.35 } },
            splitLine: { distance: -18, length: 12, lineStyle: { opacity: 0.5 } },
            axisLabel: { distance: -26, color: 'rgba(255,255,255,0.65)' },
            pointer: { length: '62%', width: 5 },
            detail: {
              valueAnimation: true,
              formatter: '{value}%',
              color: 'rgba(255,255,255,0.9)',
            },
            data: [{ value: Number(v.toFixed(1)), name: 'entropy' }],
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
