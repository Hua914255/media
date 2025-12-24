<template>
  <div class="card chart-card">
    <div class="chart-head">
      <div>
        <div class="title">Semantic River</div>
        <div class="sub">PCA 语义空间演化 (x/y)</div>
      </div>
      <div class="mini">
        <span class="pill" v-if="loading">Loading DB...</span>
        <span class="pill" v-else>DB {{ totalStaticPoints }} / Cur {{ points.length }}</span>
      </div>
    </div>

    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<script>
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { ScatterChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useStoryStore } from '../../store/storyStore'
import { mapState, mapActions } from 'pinia'

echarts.use([ScatterChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

export default {
  name: 'SemanticSpaceChart',
  components: { VChart },
  props: {
    // points: [{x, y, author, turn, text}]
    points: { type: Array, default: () => [] },
  },
  data() {
    return {
      bgPoints: [], // 静态背景点
    }
  },
  computed: {
    ...mapState(useStoryStore, ['staticData']),
    
    loading() {
      return !this.staticData
    },
    
    totalStaticPoints() {
      return this.bgPoints.length
    },

    option() {
      // 1. 准备当前故事的点和连线
      const currentPoints = this.points
        .filter(p => p.x !== undefined && p.x !== null)
        .map(p => [Number(p.x), Number(p.y), p.turn, p.text])

      // 2. 背景点 (灰色)
      // 为了性能，只取前 2000 个？或者全部
      // staticData is object { story_id: [steps...] }
      
      return {
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            if (params.seriesName === 'Background') {
               return `History Point<br/>(Static DB)`
            }
            const [x, y, t, txt] = params.value
            const shortTxt = txt && txt.length > 20 ? txt.slice(0, 20) + '...' : txt
            return `T${t}: ${shortTxt}<br/>x: ${Number(x).toFixed(2)}<br/>y: ${Number(y).toFixed(2)}`
          },
        },
        grid: { left: 30, right: 30, top: 30, bottom: 30 },
        xAxis: {
          type: 'value',
          scale: true, // 不强制从0开始
          axisLabel: { show: false }, // 隐藏坐标轴数字，更像地图
          splitLine: { show: false },
        },
        yAxis: {
          type: 'value',
          scale: true,
          axisLabel: { show: false },
          splitLine: { show: false },
        },
        series: [
          // 背景系列 (大量散点)
          {
            name: 'Background',
            type: 'scatter',
            data: this.bgPoints,
            symbolSize: 4,
            itemStyle: { color: 'rgba(255, 255, 255, 0.05)' },
            silent: true, // 静态点不交互，提升性能
            large: true,  // 开启大数据量优化
          },
          // 当前故事连线
          {
            name: 'Trajectory',
            type: 'line',
            data: currentPoints,
            smooth: true,
            lineStyle: { color: '#646cff', width: 2, opacity: 0.8 },
            symbol: 'none',
            z: 9, 
          },
          // 当前故事散点
          {
            name: 'Current',
            type: 'scatter',
            data: currentPoints,
            symbolSize: 12,
            itemStyle: { 
                color: (params) => {
                    // 最后一个点高亮
                    if (params.dataIndex === currentPoints.length - 1) return '#ffffff' 
                    return '#646cff'
                },
                borderColor: '#ffffff',
                borderWidth: 1
            },
            z: 10,
          },
        ],
      }
    },
  },
  watch: {
    staticData: {
      immediate: true,
      handler(val) {
        if (!val) return
        // 解析 staticData: { story_id: [ {x, y, ...}, ... ] }
        const allPts = []
        Object.values(val).forEach(steps => {
          steps.forEach(s => {
             // 过滤掉没有坐标的点
             if (s.x !== undefined && s.y !== undefined) {
               allPts.push([Number(s.x), Number(s.y)])
             }
          })
        })
        this.bgPoints = Object.freeze(allPts) // freeze 提升性能
      }
    }
  },
  mounted() {
    this.fetchStaticData()
  },
  methods: {
    ...mapActions(useStoryStore, ['fetchStaticData'])
  }
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
