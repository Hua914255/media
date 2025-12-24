<template>
  <div class="card stat-card">
    <div class="stat-title">{{ title }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-sub" v-if="sub">{{ sub }}</div>
    <slot />
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    title: { type: String, required: true },
    value: { type: [String, Number], required: true },
    sub: { type: String, default: '' },
  },
}
</script>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.stat-title {
  font-size: 12px;
  opacity: 0.8;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.2px;
}
.stat-sub {
  font-size: 12px;
  opacity: 0.7;
}
</style>
