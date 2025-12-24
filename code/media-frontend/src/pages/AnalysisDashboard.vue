<template>
  <div class="analysis-page">
    <div class="header">
      <h2>Data Insight Lab</h2>
      
      <!-- Filter Controls -->
      <!-- Filter Controls -->
      <div class="controls">
         <div 
           v-for="(ds, index) in allDatasets"
           :key="ds"
           class="toggle" 
           :class="{active: filters[ds]}" 
           :style="{ borderBottom: filters[ds] ? `3px solid ${colors[index % colors.length]}` : 'none' }"
           @click="filters[ds] = !filters[ds]"
         >{{ ds }}</div>
         
         <div 
           class="toggle story" 
           :class="{active: filters.Story}" 
           @click="filters.Story = !filters.Story"
         >Current Story</div>
      </div>

      <div class="stats" v-if="points.length">
        <span class="badge exp1">Exp1: {{ count.Exp1 }}</span>
        <span class="badge exp2">Exp2: {{ count.Exp2 }}</span>
        <span class="badge exp4">Exp4: {{ count.Exp4 }}</span>
      </div>
    </div>
    
    <div class="chart-container">
       <div class="loading" v-if="loading">Loading massive dataset...</div>
       <VChart class="chart" :option="option" autoresize />
    </div>
  </div>
</template>

<script>
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { ScatterChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import http from '../api/http'
import { useStoryStore } from '../store/storyStore'
import { mapState } from 'pinia'

echarts.use([ScatterChart, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, CanvasRenderer])

export default {
  name: 'AnalysisDashboard',
  components: { VChart },
  data() {
    return {
      points: [],
      loading: false,
      // 动态过滤器
      filters: {
        Story: true
      },
      // 颜色池
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
    }
  },
  computed: {
    ...mapState(useStoryStore, {
        storyTurns: 'turns'
    }),
    // 动态提取所有 dataset 名称
    allDatasets() {
      const sets = new Set()
      this.points.forEach(p => {
        if (p.dataset) sets.add(p.dataset)
      })
      return Array.from(sets).sort()
    },
    count() {
      const c = {}
      this.allDatasets.forEach(d => c[d] = 0)
      this.points.forEach(p => {
        if (c[p.dataset] !== undefined) c[p.dataset]++
      })
      return c
    },
    option() {
      // 1. 构建 Series
      const seriesList = []
      
      this.allDatasets.forEach((dsName, index) => {
        // 如果被过滤掉了，就返回空数据，但保留 series 以防图表抖动
        if (!this.filters[dsName]) return
        
        const data = []
        this.points.forEach(p => {
          if (p.dataset === dsName) {
            data.push([p.x, p.y, p.text, p.type, p.id])
          }
        })
        
        seriesList.push({
          name: dsName,
          type: 'scatter',
          symbolSize: 6,
          itemStyle: { 
            color: this.colors[index % this.colors.length], 
            opacity: 0.6 
          },
          data: data
        })
      })

      // 2. 当前故事轨迹
      const storyData = this.storyTurns.map(t => [t.x, t.y, t.text, 'current_story', `Turn ${t.turn}`])
      if (this.filters.Story) {
        seriesList.push({
            name: 'Your Story',
            type: 'line',
            symbol: 'circle',
            symbolSize: 10,
            lineStyle: { width: 4, color: '#fff', shadowBlur: 10, shadowColor: '#fff' },
            itemStyle: { color: '#fff', borderColor: '#ff00ff', borderWidth: 2 },
            z: 100, // Top layer
            data: storyData
        })
      }

      return {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const [, , txt, type, id] = params.value
            if (!txt) return ''
            return `<b>${params.seriesName}</b><br/>ID: ${id}<br/>Type: ${type}<br/>Text: ${txt.substring(0, 100)}...`
          }
        },
        legend: {
          show: false // 使用自定义控件
        },
        grid: {
          top: 60, bottom: 60, left: 40, right: 40
        },
        xAxis: { 
          type: 'value', 
          scale: true, 
          splitLine: { show: false },
          axisLabel: { color: '#666' }
        },
        yAxis: { 
          type: 'value', 
          scale: true, 
          splitLine: { lineStyle: { color: '#333' } },
          axisLabel: { color: '#666' }
        },
        dataZoom: [
          { type: 'inside' },
          { type: 'slider', bottom: 10, textStyle: { color: '#ccc' } }
        ],
        series: seriesList
      }
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const payload = await http.get('/analysis/all-data')
        // 后端现在返回的是 { experiment_name:..., data: { story_id: { ... rounds: [] } } }
        // 我们需要把它展平成 scatter points
        
        const flatPoints = []
        
        // 兼容新旧格式
        // 如果直接是 List (旧接口)
        if (Array.isArray(payload)) {
            this.points = payload
        } 
        // 如果是 Dict (新接口: dynamic analysis)
        else if (payload.data) {
            Object.values(payload.data).forEach(story => {
                const datasetName = payload.experiment_name || "Dataset"
                // 暂时用 story_id 的前缀或者默认名
                // 为了区分 Human 和 AI，我们需要在这个层级做更细的区分
                // 但是后端合并时，把 human.json 和 ai.json 合并到了同一个大 dict
                // 导致原本的 json 文件名信息丢失了...
                
                // 临时补救：后端没有透传 "source" (Human/AI)
                // 我们可以根据 story type 猜，或者所有都显示出来先
                
                // 更好方案：所有数据统一展示
                const turns = story.rounds || []
                turns.forEach(t => {
                   if (t.x !== undefined && t.y !== undefined) {
                       flatPoints.push({
                           x: t.x, 
                           y: t.y, 
                           text: t.text || story.original_sentence, 
                           type: t.author || 'unknown', 
                           id: story.story_id,
                           // Prefer datasetName if available
                           dataset: datasetName || (t.author === 'ai' ? 'AI Group' : 'Human Group') 
                       })
                       // Hack to use datasetName just to satisfy linter if not used above
                       // But actually we should verify if datasetName can be used
                       // if (false) console.log(datasetName);
                   }
                })
            })
            this.points = flatPoints
            
            // 初始化 filters
            this.allDatasets.forEach(d => {
                this.filters[d] = true
            })
        }
        
      } catch (e) {
        console.error('Fetch analysis data failed:', e)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.analysis-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #000;
  color: #fff;
}
.header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #111;
  border-bottom: 1px solid #333;
}
.controls {
    display: flex;
    gap: 10px;
}
.toggle {
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    border: 1px solid transparent;
    opacity: 0.5;
    transition: all 0.2s;
    background: #222;
}
.toggle:hover {
    opacity: 0.8;
}
.toggle.active {
    opacity: 1;
    font-weight: bold;
    border-color: rgba(255,255,255,0.3);
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
.toggle.exp1.active { background: #5470c6; color: white; }
.toggle.exp2.active { background: #91cc75; color: #000; }
.toggle.exp4.active { background: #fac858; color: #000; }
.toggle.story.active { 
    background: transparent; 
    border-color: #ff00ff; 
    color: #ff00ff; 
    box-shadow: 0 0 15px rgba(255,0,255, 0.4);
}

.chart-container {
  flex: 1;
  position: relative;
}
.chart {
  width: 100%;
  height: 100%;
}
.loading {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  color: #888;
}
.badge {
  margin-left: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}
.exp1 { background: #5470c6; color: white; }
.exp2 { background: #91cc75; color: #000; }
.exp4 { background: #fac858; color: #000; }
</style>
