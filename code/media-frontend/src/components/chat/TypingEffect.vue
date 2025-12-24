<template>
  <span>{{ displayedText }}</span>
</template>

<script>
export default {
  name: 'TypingEffect',
  props: {
    text: { type: String, required: true },
    speed: { type: Number, default: 30 }, // ms per char
  },
  data() {
    return {
      displayedText: '',
      timer: null,
    }
  },
  watch: {
    text: {
      immediate: true,
      handler(val) {
        if (!val) {
          this.displayedText = ''
          return
        }
        // 如果已经是完整显示的，就不重置动画了（避免滚动时反复打字）
        // 只有当新文本比当前显示的长，且是追加的时候才动画
        // 简单起见：每次 text 变动，如果是增量变动，就从当前位置继续打
        if (val.startsWith(this.displayedText) && this.displayedText.length > 0) {
           this.typeNext()
        } else {
           // 全新的文本，重置
           this.displayedText = ''
           this.typeNext()
        }
      },
    },
  },
  beforeUnmount() {
    clearTimeout(this.timer)
  },
  methods: {
    typeNext() {
      clearTimeout(this.timer)
      if (this.displayedText.length < this.text.length) {
        // 计算下一个要显示的字符索引
        const nextChar = this.text[this.displayedText.length]
        this.displayedText += nextChar
        
        // 随机速度增加真实感
        const randomSpeed = this.speed + (Math.random() - 0.5) * 20
        this.timer = setTimeout(this.typeNext, Math.max(10, randomSpeed))
      } else {
        // 完成
        this.$emit('done')
      }
    },
  },
}
</script>
