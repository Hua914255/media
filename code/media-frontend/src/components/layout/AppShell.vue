<template>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo-dot"></div>
        <div class="brand-text">
          <div class="brand-title">Story Lab</div>
          <div class="brand-sub">Semantic Flow & Creative Entropy Dashboard</div>
        </div>
      </div>

      <div class="topbar-actions">
        <slot name="actions" />
      </div>
    </header>

    <main class="main">
      <section class="left">
        <slot name="left" />
      </section>

      <section class="right">
        <slot name="right" />
      </section>
    </main>
  </div>
</template>

<script>
export default { name: 'AppShell' }
</script>

<style scoped>
.shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(125, 211, 252, 1), rgba(167, 139, 250, 1));
  box-shadow: 0 0 16px rgba(167, 139, 250, 0.35);
}
.brand-title {
  font-weight: 800;
  letter-spacing: 0.2px;
}
.brand-sub {
  font-size: 12px;
  opacity: 0.7;
}
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main {
  flex: 1;
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 14px;
  padding: 14px;
  overflow: hidden;
}
.left, .right {
  overflow: hidden;
  min-height: 0;
}
.left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.right {
  display: grid;
  grid-template-rows: 1fr 280px;
  gap: 12px;
}
@media (max-width: 980px) {
  .main { grid-template-columns: 1fr; }
  .right { grid-template-rows: 360px 280px; }
}
</style>
