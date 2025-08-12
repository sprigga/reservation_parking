<template>
  <div>
    <div style="margin-bottom: 12px;">
      <button @click="refresh">重新整理</button>
    </div>
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>車位</th>
          <th>姓名</th>
          <th>戶別</th>
          <th>手機</th>
          <th>開始</th>
          <th>結束</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reservations" :key="r.id">
          <td>{{ r.id }}</td>
          <td>{{ findSpotNumber(r.spot_id) }}</td>
          <td>{{ r.name }}</td>
          <td>{{ r.household }}</td>
          <td>{{ r.phone }}</td>
          <td>{{ formatDate(r.start_time) }}</td>
          <td>{{ formatDate(r.end_time) }}</td>
          <td>
            <button @click="remove(r.id)">取消</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const reservations = ref([])
const spots = ref([])

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString()
}

function findSpotNumber(spot_id) {
  const s = spots.value.find(s => s.id === spot_id)
  return s ? s.spot_number : spot_id
}

async function refresh() {
  const [r1, r2] = await Promise.all([
    api.get('/reservations'),
    api.get('/spots'),
  ])
  reservations.value = r1.data
  spots.value = r2.data
}

async function remove(id) {
  if (!confirm(`確定要取消預約 #${id} 嗎？`)) return
  try {
    await api.delete(`/reservations/${id}`)
    await refresh()
  } catch (err) {
    alert(err?.response?.data?.detail || err.message)
  }
}

onMounted(() => refresh())
</script>
