<template>
  <main style="padding: 20px; max-width: 900px; margin: 0 auto;">
    <h1>社區公共車位預約系統</h1>

    <section style="margin-top: 24px; padding: 16px; border: 1px solid #ddd; border-radius: 8px;">
      <h2>預約表單</h2>
      <ReservationForm />
    </section>

    <section style="margin-top: 24px; padding: 16px; border: 1px solid #ddd; border-radius: 8px;">
      <h2>管理者模式</h2>
      <Admin />
    </section>
  </main>
</template>

<script setup>
import ReservationForm from './pages/ReservationForm.vue'
import Admin from './pages/Admin.vue'
</script>

<style>
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
label { display: block; margin-top: 8px; }
input, select { padding: 6px 8px; margin-top: 4px; }
button { padding: 6px 12px; margin-top: 12px; }
.table { border-collapse: collapse; width: 100%; }
.table th, .table td { border: 1px solid #ddd; padding: 8px; }
.table th { background: #f7f7f7; }
</style>
