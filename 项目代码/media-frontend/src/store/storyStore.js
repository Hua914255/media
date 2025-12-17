import { defineStore } from 'pinia'
import { createStory, continueStory, getStory } from '../api/story'

function clamp01(x) {
  if (Number.isNaN(x)) return 0
  return Math.max(0, Math.min(1, x))
}

export const useStoryStore = defineStore('story', {
  state: () => ({
    storyId: null,
    turns: [], // {story_id, turn, author, text, flow_score, entropy_score}
    loading: false,
    error: null,

    // replay
    replayIndex: 0,
    replayPlaying: false,
    replaySpeedMs: 450,
  }),

  getters: {
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
    async ensureStory() {
      if (this.storyId) return this.storyId
      const res = await createStory()
      this.storyId = res.story_id
      this.turns = []
      this.error = null
      return this.storyId
    },

    async loadStory(storyId) {
      this.loading = true
      this.error = null
      try {
        const res = await getStory(storyId)
        this.storyId = res.story_id
        this.turns = Array.isArray(res.turns) ? res.turns : []
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
        // 后端返回的 new_turns 可能 turn=-1（mock），但我们这里直接 concat，展示就行
        this.turns = this.turns.concat(newTurns)
      } catch (e) {
        this.error = e?.message || 'Continue failed'
      } finally {
        this.loading = false
      }
    },

    pushTurnFromWS(item) {
      // item should include: story_id, turn, author, text, flow_score, entropy_score
      this.turns = this.turns.concat([item])
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
  },
})
