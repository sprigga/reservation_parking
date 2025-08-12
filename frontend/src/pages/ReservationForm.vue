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

      <fieldset style="margin-top: 8px;">
        <legend>預約開始時間（24小時制，30 分鐘一格）</legend>
        <div style="display:flex; gap:8px; align-items:center; flex-wrap: wrap;">
          <input type="date" v-model="form.start_date" required />
          <select v-model="form.start_hm" required>
            <option value="" disabled>選擇時間</option>
            <option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </fieldset>

      <fieldset style="margin-top: 8px;">
        <legend>預約結束時間（24小時制，30 分鐘一格）</legend>
        <div style="display:flex; gap:8px; align-items:center; flex-wrap: wrap;">
          <input type="date" v-model="form.end_date" required />
          <select v-model="form.end_hm" required>
            <option value="" disabled>選擇時間</option>
            <option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </fieldset>

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
import { onMounted, reactive, ref, watch } from 'vue'
import api from '../api'

const spots = ref([])
const reservations = ref([])

const timeSlots = ref([])

const form = reactive({
  name: '',
  household: '',
  phone: '',
  spot_id: '',
  start_date: '',
  start_hm: '',
  end_date: '',
  end_hm: '',
})

function pad(n) { return n.toString().padStart(2, '0') }

function generateTimeSlots() {
  const slots = []
  for (let h = 0; h < 24; h++) {
    slots.push(`${pad(h)}:00`)
    slots.push(`${pad(h)}:30`)
  }
  timeSlots.value = slots
}

function toIsoLocal(dateStr, hmStr) {
  if (!dateStr || !hmStr) return null
  return `${dateStr}T${hmStr}:00`
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  // 顯示 24 小時格式
  return d.toLocaleString([], { hour12: false })
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

function roundUpToNext30(d) {
  const date = new Date(d)
  const m = date.getMinutes()
  if (m === 0 || m === 30) return date
  if (m < 30) {
    date.setMinutes(30, 0, 0)
  } else {
    date.setHours(date.getHours() + 1, 0, 0, 0)
  }
  return date
}

function ymd(date) {
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}`
}

function hm(date) {
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`
}

async function submit() {
  try {
    const start_iso = toIsoLocal(form.start_date, form.start_hm)
    const end_iso = toIsoLocal(form.end_date, form.end_hm)
    if (!start_iso || !end_iso) {
      alert('請選擇完整的開始與結束時間')
      return
    }
    if (new Date(end_iso) <= new Date(start_iso)) {
      alert('結束時間需晚於開始時間')
      return
    }

    const payload = {
      name: form.name,
      household: form.household,
      phone: form.phone,
      spot_id: Number(form.spot_id),
      start_time: start_iso,
      end_time: end_iso,
    }
    await api.post('/reservations', payload)
    alert('預約成功')
    await loadReservations()
  } catch (err) {
    const msg = err?.response?.data?.detail || err.message
    alert(`預約失敗：${msg}`)
  }
}

// 當開始日期變動時，自動同步結束日期為相同日期（若結束日期原本不同天）
watch(() => form.start_date, (nv) => {
  if (!nv) return
  if (form.end_date !== nv) {
    form.end_date = nv
  }
})

onMounted(async () => {
  generateTimeSlots()
  // 設定預設值：下一個 30 分鐘整點為開始，結束 +30 分鐘
  const now = new Date()
  const start = roundUpToNext30(now)
  const end = new Date(start.getTime() + 30 * 60 * 1000)
  form.start_date = ymd(start)
  form.start_hm = hm(start)
  form.end_date = ymd(end)
  form.end_hm = hm(end)

  await loadSpots()
  await loadReservations()
})
</script>
