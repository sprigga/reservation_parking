<template>
  <div>
    <form @submit.prevent="submit">
      <label>
        姓名
        <input v-model="form.name" required />
      </label>
      <label>
        戶別
        <input v-model="form.household" required />
      </label>
      <label>
        手機
        <input v-model="form.phone" required />
      </label>
      <label>
        預約車位號碼
        <select v-model.number="form.spot_id" required>
          <option value="" disabled>請選擇車位</option>
          <option v-for="s in spots" :key="s.id" :value="s.id">{{ s.spot_number }}</option>
        </select>
      </label>
      <label>
        預約開始時間
        <input type="datetime-local" v-model="form.start_time" required />
      </label>
      <label>
        預約結束時間
        <input type="datetime-local" v-model="form.end_time" required />
      </label>
      <div>
        <button type="submit">送出預約</button>
      </div>
    </form>

    <div style="margin-top: 16px;">
      <h3>目前預約（依開始時間）</h3>
      <table class="table">
        <thead>
          <tr>
            <th>車位</th>
            <th>姓名</th>
            <th>戶別</th>
            <th>手機</th>
            <th>開始</th>
            <th>結束</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reservations" :key="r.id">
            <td>{{ findSpotNumber(r.spot_id) }}</td>
            <td>{{ r.name }}</td>
            <td>{{ r.household }}</td>
            <td>{{ r.phone }}</td>
            <td>{{ formatDate(r.start_time) }}</td>
            <td>{{ formatDate(r.end_time) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../api'

const spots = ref([])
const reservations = ref([])

const form = reactive({
  name: '',
  household: '',
  phone: '',
  spot_id: '',
  start_time: '',
  end_time: '',
})

function toIsoLocal(datetimeLocal) {
  // Convert input type=datetime-local value to ISO string (no timezone conversion) for backend
  // Assume local time: append ':00' seconds if missing
  if (!datetimeLocal) return null
  const pad = (n) => n.toString().padStart(2, '0')
  const d = new Date(datetimeLocal)
  // use local components
  const yyyy = d.getFullYear()
  const MM = pad(d.getMonth() + 1)
  const dd = pad(d.getDate())
  const hh = pad(d.getHours())
  const mm = pad(d.getMinutes())
  const ss = pad(d.getSeconds())
  return `${yyyy}-${MM}-${dd}T${hh}:${mm}:${ss}`
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString()
}

function findSpotNumber(spot_id) {
  const s = spots.value.find(s => s.id === spot_id)
  return s ? s.spot_number : spot_id
}

async function loadSpots() {
  const { data } = await api.get('/spots')
  spots.value = data
}

async function loadReservations() {
  const { data } = await api.get('/reservations')
  reservations.value = data
}

async function submit() {
  try {
    const payload = {
      name: form.name,
      household: form.household,
      phone: form.phone,
      spot_id: Number(form.spot_id),
      start_time: toIsoLocal(form.start_time),
      end_time: toIsoLocal(form.end_time),
    }
    await api.post('/reservations', payload)
    alert('預約成功')
    await loadReservations()
  } catch (err) {
    const msg = err?.response?.data?.detail || err.message
    alert(`預約失敗：${msg}`)
  }
}

onMounted(async () => {
  await loadSpots()
  await loadReservations()
})
</script>
