<template>
  <div class="list" ref="listEl">
    <div
      v-for="(m, idx) in visibleMessages"
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
      <div class="bubble">
         <TypingEffect 
            v-if="m.author === 'ai'" 
            :text="m.text" 
            :speed="30"
            @done="onTypeUpdate" 
         />
         <span v-else>{{ m.text }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import TypingEffect from './TypingEffect.vue'

export default {
  name: 'MessageList',
  components: { TypingEffect },

  props: {
    messages: { type: Array, default: () => [] },
  },
  data() {
    return {
      visibleCount: 0,
    }
  },
  computed: {
    visibleMessages() {
        return this.messages.slice(0, this.visibleCount)
    }
  },
  watch: {
    messages: {
      immediate: true,
      handler(newVal, oldVal) {
        const oldLen = oldVal ? oldVal.length : 0
        const newLen = newVal ? newVal.length : 0
        
        // 如果是重置（newLen=0）或变小，直接重置
        if (newLen === 0) {
            this.visibleCount = 0
            return
        }
        
        // 如果是新增消息
        if (newLen > oldLen) {
            // 如果原来的 visibleCount 已经满了，说明之前的都打完了，现在的可以直接显示第一条新的
            // 或者如果这是第一次加载（oldLen=0），也只显示第一条
            if (this.visibleCount === oldLen) {
                // 开始打下一条
                this.visibleCount = oldLen + 1
            }
            // 如果之前的还没打完，visibleCount不用动，打完那条之后 onTypeUpdate 会触发下一条
        }
      }
    },
    visibleCount(val) {
        // 当显示的条数增加时，检查最新显示的那条是否是 Human
        // Human 消息没有 TypingEffect，不会触发 done 事件，所以需要手动触发下一条
        if (val > 0 && val <= this.messages.length) {
            const lastMsg = this.messages[val - 1]
            if (lastMsg && lastMsg.author !== 'ai') {
                // 是人类消息，直接调用完成逻辑（可以加点延迟模拟阅读节奏）
                this.onTypeUpdate()
            }
        }
    },
  },
  methods: {
    fmt(x) {
      const n = Number(x ?? 0)
      return Number.isFinite(n) ? n.toFixed(2) : '0.00'
    },
    onTypeUpdate() {
        // 完成打字
        this.scrollToBottom()
        
        // 如果还有未显示的消息，显示下一条
        if (this.visibleCount < this.messages.length) {
            // 小延迟增加真实感
            setTimeout(() => {
                this.visibleCount++
            }, 500) // 500ms delay between AI turns
        }
    },
    scrollToBottom() {
        this.$nextTick(() => {
            const el = this.$refs.listEl
            if (el) el.scrollTop = el.scrollHeight
        })
    }
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
