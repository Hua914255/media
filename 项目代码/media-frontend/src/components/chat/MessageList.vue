<template>
  <div class="list" ref="listEl">
    <div
      v-for="(m, idx) in messages"
      :key="idx"
      class="msg"
      :class="m.author === 'human' ? 'human' : 'ai'"
    >
      <div class="meta">
        <span class="tag">{{ m.author === 'human' ? 'Human' : 'AI' }}</span>
        <span class="turn">T{{ m.turn }}</span>
        <span class="scores">
          flow {{ fmt(m.flow_score) }} · entropy {{ fmt(m.entropy_score) }}
        </span>
      </div>
      <div class="bubble">{{ m.text }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MessageList',
  props: {
    messages: { type: Array, default: () => [] },
  },
  watch: {
    messages() {
      this.$nextTick(() => {
        const el = this.$refs.listEl
        if (el) el.scrollTop = el.scrollHeight
      })
    },
  },
  methods: {
    fmt(x) {
      const n = Number(x ?? 0)
      return Number.isFinite(n) ? n.toFixed(2) : '0.00'
    },
  },
}
</script>

<style scoped>
.list {
  flex: 1;
  overflow: auto;
  padding: 10px;
  border-radius: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
}
.msg {
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  opacity: 0.85;
}
.tag {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
}
.turn { opacity: 0.8; }
.scores { opacity: 0.7; margin-left: auto; }

.bubble {
  padding: 10px 12px;
  border-radius: 14px;
  line-height: 1.45;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
}
.msg.human .bubble {
  background: rgba(56, 189, 248, 0.08);
}
.msg.ai .bubble {
  background: rgba(167, 139, 250, 0.08);
}
</style>
