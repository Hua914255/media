<template>
  <div class="card chart-card" :class="{ heartbeat: value > 0.8 }">
    <div class="chart-head">
      <div>
        <div class="title" :style="{color: value > 0.8 ? '#ff4d4d' : ''}">Creative Entropy</div>
        <div class="sub">实时仪表盘：越高越“出乎意料”</div>
      </div>
      <div class="mini">
        <span class="pill" :class="{ high: value > 0.8 }">now {{ value.toFixed(2) }}</span>
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
      const isHigh = this.value > 0.8
      return {
        tooltip: { formatter: '{a}<br/>{b}: {c}%' },
        series: [
          {
            name: 'entropy',
            type: 'gauge',
            itemStyle: {
                color: isHigh ? '#ff4d4d' : '#91cc75',
                shadowBlur: isHigh ? 10 : 0,
                shadowColor: '#ff4d4d'
            },
            progress: { show: true, width: 12 },
            startAngle: 200,
            endAngle: -20,
            min: 0,
            max: 100,
            splitNumber: 5,

            axisLine: { lineStyle: { width: 12, opacity: 0.35 } },
            axisTick: { distance: -18, length: 6, lineStyle: { opacity: 0.35 } },
            splitLine: { distance: -18, length: 12, lineStyle: { opacity: 0.5 } },
            axisLabel: { distance: -26, color: 'rgba(255,255,255,0.65)' },
            pointer: { length: '62%', width: 5 },
            detail: {
              valueAnimation: true,
              formatter: '{value}%',
              color: isHigh ? '#ff4d4d' : 'rgba(255,255,255,0.9)',
              fontSize: isHigh ? 24 : 14,
              fontWeight: isHigh ? 'bold' : 'normal',
              offsetCenter: [0, '70%'] // Move down a bit
            },
            data: [{ value: Number(v.toFixed(1)), name: isHigh ? '!!!' : 'entropy' }],
          },
        ],
      }
    },
  },
}
</script>

<style scoped>
.chart-card { 
    height: 100%; 
    display: flex; 
    flex-direction: column; 
    overflow: hidden; 
    transition: all 0.5s;
}
/* Heartbeat Effect for the whole card */
.chart-card.heartbeat {
    border-color: rgba(255, 77, 77, 0.6);
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) inset;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

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
  transition: all 0.3s;
}
.pill.high {
    background: #ff4d4d;
    color: white;
    box-shadow: 0 0 10px #ff4d4d;
}
</style>
