import { defineStore } from 'pinia'
import { createStory, continueStory, getStory } from '../api/story'

function clamp01(x) {
  if (Number.isNaN(x)) return 0
  return Math.max(0, Math.min(1, x))
}

export const useStoryStore = defineStore('story', {
  state: () => ({
    storyId: localStorage.getItem('story_id') || null,
    turns: JSON.parse(localStorage.getItem('story_turns') || '[]'),
    loading: false,
    error: null,

    // replay
    replayIndex: 0,
    replayPlaying: false,
    replaySpeedMs: 450,
    
    // visualization
    staticData: null,
  }),

  getters: {
    // ... same getters
    flowSeries(state) {
      return state.turns.map((t) => clamp01(Number(t.flow_score ?? 0)))
    },
    entropySeries(state) {
      return state.turns.map((t) => clamp01(Number(t.entropy_score ?? 0)))
    },
    labels(state) {
      return state.turns.map((t) => `T${t.turn}`)
    },
    latestEntropy(state) {
      const last = state.turns[state.turns.length - 1]
      return clamp01(Number(last?.entropy_score ?? 0))
    },
    visibleTurns(state) {
      // for replay mode: show first replayIndex turns
      if (!state.replayPlaying && state.replayIndex === 0) return state.turns
      return state.turns.slice(0, Math.max(0, state.replayIndex))
    },
  },

  actions: {
    saveState() {
        if (this.storyId) localStorage.setItem('story_id', this.storyId)
        localStorage.setItem('story_turns', JSON.stringify(this.turns))
    },

    async ensureStory() {
      if (this.storyId) return this.storyId
      const res = await createStory()
      this.storyId = res.story_id
      this.turns = []
      this.error = null
      this.saveState()
      return this.storyId
    },

    async loadStory(storyId) {
      this.loading = true
      this.error = null
      try {
        const res = await getStory(storyId)
        this.storyId = res.story_id
        this.turns = Array.isArray(res.turns) ? res.turns : []
        this.saveState()
      } catch (e) {
        this.error = e?.message || 'Load story failed'
      } finally {
        this.loading = false
      }
    },

    async restContinue({ userText, rounds = 1, mode = 'human_ai' }) {
      this.loading = true
      this.error = null
      try {
        const sid = await this.ensureStory()
        const res = await continueStory({
          story_id: sid,
          user_text: userText,
          rounds,
          mode,
        })
        const newTurns = Array.isArray(res.new_turns) ? res.new_turns : []
        this.turns = this.turns.concat(newTurns)
        this.saveState()
      } catch (e) {
        this.error = e?.message || 'Continue failed'
      } finally {
        this.loading = false
      }
    },

    pushTurnFromWS(item) {
      this.turns = this.turns.concat([item])
      this.saveState()
    },

    resetReplay() {
      this.replayIndex = 0
      this.replayPlaying = false
    },

    async playReplay() {
      this.replayPlaying = true
      this.replayIndex = 0
      while (this.replayPlaying && this.replayIndex < this.turns.length) {
        await new Promise((r) => setTimeout(r, this.replaySpeedMs))
        this.replayIndex += 1
      }
      this.replayPlaying = false
    },

    pauseReplay() {
      this.replayPlaying = false
    },

    async fetchStaticData() {
      // 避免重复请求
      if (this.staticData && Object.keys(this.staticData).length > 0) return
      try {
        // 动态导入，避免循环引用
        const { getStaticData } = await import('../api/story')
        const data = await getStaticData()
        this.staticData = data
      } catch (e) {
        console.warn('Fetch static data failed:', e)
      }
    },
  },
})
