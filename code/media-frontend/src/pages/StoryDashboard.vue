<template>
  <AppShell>
    <template #actions>
      <button class="btn" @click="gotoReplay" :disabled="!storyId">Replay</button>
      <button class="btn" @click="newStory">New Story</button>
    </template>

    <template #left>
      <ChatPanel
        :messages="turns"
        :busy="loading"
        :error="error"
        @send="onSend"
        @clear="onClear"
        @toggleStreaming="onToggleStreaming"
      />
    </template>

    <template #right>
      <FlowLineChart :labels="labels" :series="flowSeries" />
      <div class="bottom-grid">
        <EntropyGauge :value="latestEntropy" />
        
        <div class="visual-tabs-container">
            <div class="visual-tabs">
                <div class="tab" :class="{active: viewMode==='semantic'}" @click="viewMode='semantic'">River</div>
                <div class="tab" :class="{active: viewMode==='compare'}" @click="viewMode='compare'">Scatter</div>
            </div>
            
            <div class="visual-content">
                <SemanticSpaceChart v-if="viewMode==='semantic'" :points="semanticPoints" />
                <CompareScatter v-else :points="scatterPoints" />
            </div>
        </div>
      </div>
    </template>
  </AppShell>
</template>

<script>
import AppShell from '../components/layout/AppShell.vue'
import ChatPanel from '../components/chat/ChatPanel.vue'
import FlowLineChart from '../components/charts/FlowLineChart.vue'
import EntropyGauge from '../components/charts/EntropyGauge.vue'
import CompareScatter from '../components/charts/CompareScatter.vue'
import SemanticSpaceChart from '../components/charts/SemanticSpaceChart.vue'

import { useStoryStore } from '../store/storyStore'
import { openStoryWS } from '../api/ws'
import { mapState, mapGetters } from 'pinia'

export default {
  name: 'StoryDashboard',
  components: { AppShell, ChatPanel, FlowLineChart, EntropyGauge, CompareScatter, SemanticSpaceChart },
  data() {
    return {
      streaming: true,
      ws: null,
      viewMode: 'semantic', // 'semantic' | 'compare'
    }
  },
  computed: {
    ...mapState(useStoryStore, ['storyId', 'turns', 'loading', 'error']),
    ...mapGetters(useStoryStore, ['labels', 'flowSeries', 'latestEntropy', 'entropySeries']),

    scatterPoints() {
      return this.turns.map((t) => ({
        flow: Number(t.flow_score ?? 0),
        entropy: Number(t.entropy_score ?? 0),
        author: t.author,
        turn: t.turn,
      }))
    },
    semanticPoints() {
      return this.turns.map((t) => ({
        x: t.x,
        y: t.y,
        text: t.text,
        author: t.author,
        turn: t.turn,
      }))
    },
  },
  beforeUnmount() {
    if (this.ws) this.ws.close()
  },
  methods: {
    store() {
      return useStoryStore()
    },

    async ensureWS() {
      const s = this.store()
      const sid = await s.ensureStory()

      // 已连接就直接返回
      if (this.ws && this.ws.readyState === WebSocket.OPEN) return this.ws

      // 如果正在连接，等待连接完成
      if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
        await new Promise((resolve, reject) => {
          const timer = setInterval(() => {
            if (!this.ws) {
              clearInterval(timer)
              reject(new Error('WS closed'))
              return
            }
            if (this.ws.readyState === WebSocket.OPEN) {
              clearInterval(timer)
              resolve()
              return
            }
            if (this.ws.readyState === WebSocket.CLOSED) {
              clearInterval(timer)
              reject(new Error('WS closed'))
            }
          }, 50)

          setTimeout(() => {
            clearInterval(timer)
            reject(new Error('WS open timeout'))
          }, 5000)
        })
        return this.ws
      }

      // 否则新建连接，并等待 onopen
      await new Promise((resolve, reject) => {
        const ws = openStoryWS({
          storyId: sid,
          onMessage: (item) => {
            this.store().pushTurnFromWS(item)
          },
          onOpen: () => resolve(),
          onClose: () => {},
          onError: (e) => reject(e || new Error('WS error')),
        })

        this.ws = ws

        setTimeout(() => {
          reject(new Error('WS open timeout'))
        }, 5000)
      })

      return this.ws
    },

    async onSend({ text, rounds, mode }) {
      const s = this.store()

      if (this.streaming) {
        try {
          const ws = await this.ensureWS()
          ws.send(JSON.stringify({ user_text: text, rounds, mode }))
        } catch (e) {
          console.warn('[WS] send failed, fallback to REST:', e)
          await s.restContinue({ userText: text, rounds, mode })
        }
      } else {
        await s.restContinue({ userText: text, rounds, mode })
      }
    },

    onClear() {
      const s = this.store()
      s.turns = []
      s.error = null
    },

    onToggleStreaming(v) {
      this.streaming = !!v
      if (!this.streaming && this.ws) {
        this.ws.close()
        this.ws = null
      }
    },

    async newStory() {
      const s = this.store()
      s.storyId = null
      s.turns = []
      s.error = null

      if (this.ws) {
        this.ws.close()
        this.ws = null
      }

      await s.ensureStory()

      // 可选：如果你想一进来就先连上 WS（体验更像实时系统）
      // if (this.streaming) await this.ensureWS()
    },

    gotoReplay() {
      if (!this.storyId) return
      this.$router.push({ name: 'StoryReplay', params: { storyId: this.storyId } })
    },
  },
}
</script>

<style scoped>
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
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: inherit;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
@media (max-width: 980px) {
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

.visual-tabs-container {
    display: flex; 
    flex-direction: column; 
    overflow: hidden; 
    /* 统一样式，类似卡片 */
    border-radius: 16px;
    /* background: rgba(30,30,30,0.6); */
}
.visual-tabs {
    display: flex;
    gap: 2px;
    background: rgba(255,255,255,0.05);
    padding: 4px;
    border-radius: 12px 12px 0 0;
}
.tab {
    flex: 1;
    text-align: center;
    padding: 6px;
    font-size: 13px;
    border-radius: 8px;
    cursor: pointer;
    opacity: 0.6;
    transition: all 0.2s;
}
.tab.active {
    background: rgba(255,255,255,0.1);
    opacity: 1;
    font-weight: bold;
}
.visual-content {
    flex: 1;
    min-height: 0;
    /* card已经有样式了，这里只需占位 */
    display: flex; 
    flex-direction: column;
}
</style>
