<template>
  <AppShell>
    <template #actions>
      <button class="btn" @click="$router.push('/')">Back</button>
      <button class="btn" @click="load">Reload</button>
    </template>

    <template #left>
      <div class="card panel">
        <div class="h">
          <div class="title">Replay Mode</div>
          <div class="sub">逐条回放 turns，图表同步增长（答辩超加分）</div>
        </div>

        <div class="row">
          <div class="control">
            <label>Speed (ms)</label>
            <input type="number" min="100" max="1500" v-model.number="speed" />
          </div>
          <div class="control">
            <label>Progress</label>
            <div class="bar">
              <div class="bar-inner" :style="{ width: pct + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="btn primary" @click="play" :disabled="playing || !turns.length">Play</button>
          <button class="btn" @click="pause" :disabled="!playing">Pause</button>
          <button class="btn" @click="reset" :disabled="!turns.length">Reset</button>
        </div>

        <div class="list">
          <div v-for="t in visibleTurns" :key="t.turn" class="item">
            <div class="meta">
              <span class="tag">{{ t.author }}</span>
              <span class="turn">T{{ t.turn }}</span>
              <span class="scores">flow {{ fmt(t.flow_score) }} · entropy {{ fmt(t.entropy_score) }}</span>
            </div>
            <div class="text">{{ t.text }}</div>
          </div>
        </div>
      </div>
    </template>

    <template #right>
      <FlowLineChart :labels="visibleLabels" :series="visibleFlow" />
      <div class="bottom-grid">
        <EntropyGauge :value="visibleEntropyNow" />
        <CompareScatter :points="visibleScatter" />
      </div>
    </template>
  </AppShell>
</template>

<script>
import AppShell from '../components/layout/AppShell.vue'
import FlowLineChart from '../components/charts/FlowLineChart.vue'
import EntropyGauge from '../components/charts/EntropyGauge.vue'
import CompareScatter from '../components/charts/CompareScatter.vue'
import { useStoryStore } from '../store/storyStore'

export default {
  name: 'StoryReplay',
  components: { AppShell, FlowLineChart, EntropyGauge, CompareScatter },
  props: {
    storyId: { type: String, required: true },
  },
  data() {
    return { speed: 450 }
  },
  computed: {
    store() { return useStoryStore() },
    turns() { return this.store.turns },
    playing() { return this.store.replayPlaying },

    visibleTurns() {
      if (!this.store.replayPlaying && this.store.replayIndex === 0) return this.turns
      return this.turns.slice(0, Math.max(0, this.store.replayIndex))
    },
    visibleLabels() { return this.visibleTurns.map((t) => `T${t.turn}`) },
    visibleFlow() { return this.visibleTurns.map((t) => Number(t.flow_score ?? 0)) },
    visibleEntropyNow() {
      const last = this.visibleTurns[this.visibleTurns.length - 1]
      return Number(last?.entropy_score ?? 0)
    },
    visibleScatter() {
      return this.visibleTurns.map((t) => ({
        flow: Number(t.flow_score ?? 0),
        entropy: Number(t.entropy_score ?? 0),
        author: t.author,
        turn: t.turn,
      }))
    },
    pct() {
      if (!this.turns.length) return 0
      return Math.round((Math.min(this.store.replayIndex, this.turns.length) / this.turns.length) * 100)
    },
  },
  async mounted() {
    await this.load()
  },
  methods: {
    fmt(x) {
      const n = Number(x ?? 0)
      return Number.isFinite(n) ? n.toFixed(2) : '0.00'
    },
    async load() {
      await this.store.loadStory(this.storyId)
      this.store.resetReplay()
    },
    play() {
      this.store.replaySpeedMs = this.speed
      this.store.playReplay()
    },
    pause() {
      this.store.pauseReplay()
    },
    reset() {
      this.store.resetReplay()
    },
  },
}
</script>

<style scoped>
.panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
}
.h .title { font-weight: 800; font-size: 16px; }
.h .sub { font-size: 12px; opacity: 0.75; margin-top: 2px; }

.row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 10px;
}
.control {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
}
.control input {
  height: 34px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  color: inherit;
  padding: 0 10px;
  outline: none;
}
.bar {
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
  overflow: hidden;
}
.bar-inner {
  height: 100%;
  background: linear-gradient(135deg, rgba(56,189,248,0.28), rgba(167,139,250,0.28));
}

.actions { display: flex; gap: 10px; justify-content: flex-end; }

.list {
  flex: 1;
  overflow: auto;
  padding: 10px;
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
}
.item { margin-bottom: 10px; display: flex; flex-direction: column; gap: 6px; }
.meta { display: flex; gap: 10px; font-size: 12px; opacity: 0.85; align-items: center; }
.tag {
  padding: 2px 8px; border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
}
.turn { opacity: 0.8; }
.scores { opacity: 0.7; margin-left: auto; }
.text {
  padding: 10px 12px;
  border-radius: 14px;
  line-height: 1.45;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
}

.bottom-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 12px;
  min-height: 0;
}
.btn {
  height: 34px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
  color: inherit;
  cursor: pointer;
}
.btn.primary {
  background: linear-gradient(135deg, rgba(56,189,248,0.25), rgba(167,139,250,0.25));
  border-color: rgba(255,255,255,0.16);
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 980px) {
  .row { grid-template-columns: 1fr; }
  .bottom-grid { grid-template-columns: 1fr; }
}
</style>
