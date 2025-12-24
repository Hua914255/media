<template>
  <div class="card chat-panel">
    <div class="header">
      <div class="title">Narrative Console</div>
      <div class="sub">输入一句话，续写并实时更新指标</div>
    </div>

    <div class="controls">
      <div class="control">
        <label>Rounds</label>
        <input type="number" min="1" max="10" v-model.number="rounds" />
      </div>

      <div class="control">
        <label>Mode</label>
        <select v-model="mode">
          <option value="human_ai">human_ai</option>
          <option value="ai_only">ai_only</option>
          <option value="human_only">human_only</option>
        </select>
      </div>

      <div class="control toggle">
        <label>Streaming</label>
        <button class="btn" :class="{ on: streaming }" @click="streaming = !streaming">
          {{ streaming ? 'ON (WS)' : 'OFF (REST)' }}
        </button>
      </div>
    </div>

    <MessageList :messages="messages" />

    <div class="composer">
      <textarea
        v-model="text"
        class="input"
        placeholder="写一句开头...（Enter 发送，Shift+Enter 换行）"
        @keydown="onKeydown"
      />
      <div class="actions">
        <button class="btn primary" :disabled="busy || !text.trim()" @click="send">
          {{ busy ? 'Running...' : 'Send' }}
        </button>
        <button class="btn" :disabled="busy" @click="$emit('clear')">Clear</button>
      </div>
    </div>

    <div class="error" v-if="error">{{ error }}</div>
  </div>
</template>

<script>
import MessageList from './MessageList.vue'

export default {
  name: 'ChatPanel',
  components: { MessageList },
  props: {
    messages: { type: Array, default: () => [] },
    busy: { type: Boolean, default: false },
    error: { type: String, default: '' },
  },
  emits: ['send', 'clear', 'toggleStreaming'],
  data() {
    return {
      text: '',
      rounds: 2,
      mode: 'human_ai',
      streaming: true,
    }
  },
  watch: {
    streaming(v) {
      this.$emit('toggleStreaming', v)
    },
  },
  methods: {
    onKeydown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        this.send()
      }
    },
    send() {
      const t = this.text.trim()
      if (!t) return
      this.$emit('send', { text: t, rounds: this.rounds, mode: this.mode })
      this.text = ''
    },
  },
}
</script>

<style scoped>
.chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
}
.header .title { font-weight: 800; font-size: 16px; }
.header .sub { font-size: 12px; opacity: 0.75; margin-top: 2px; }

.controls {
  display: grid;
  grid-template-columns: 1fr 1fr 1.2fr;
  gap: 10px;
}
.control {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
}
.control input, .control select {
  height: 34px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  color: inherit;
  padding: 0 10px;
  outline: none;
}
.control.toggle { justify-content: flex-end; }

.composer {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.input {
  min-height: 86px;
  resize: none;
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.10);
  color: inherit;
  outline: none;
}
.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.error {
  font-size: 12px;
  color: rgba(248, 113, 113, 1);
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
.btn.on {
  box-shadow: 0 0 0 2px rgba(56,189,248,0.25) inset;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
