<template>
  <div class="reservation-form">
    <form @submit.prevent="submit" class="form">
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">👤 姓名</span>
            <input 
              v-model="form.name" 
              class="form-input" 
              placeholder="請輸入您的姓名"
              required 
            />
          </label>
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-text">🏠 戶別</span>
            <input 
              v-model="form.household" 
              class="form-input" 
              placeholder="例：B1-3F"
              required 
            />
          </label>
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-text">📱 手機號碼</span>
            <input 
              v-model="form.phone" 
              class="form-input" 
              placeholder="例：0912345678"
              required 
            />
          </label>
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-text">🅿️ 預約車位號碼</span>
            <select v-model.number="form.spot_id" class="form-select" required>
              <option value="" disabled>請選擇車位</option>
              <option v-for="s in spots" :key="s.id" :value="s.id">
                {{ s.spot_number }}
              </option>
            </select>
          </label>
        </div>
      </div>

      <div class="time-section">
        <div class="time-group">
          <h4 class="time-title">
            <span class="time-icon">🕐</span>
            預約開始時間
          </h4>
          <div class="time-inputs">
            <div class="input-group">
              <label class="input-label">日期</label>
              <input 
                type="date" 
                v-model="form.start_date" 
                class="form-input date-input"
                :class="{ 'disabled': form.spot_id && form.start_date && isDateFullyBooked(form.start_date, form.spot_id) }"
                required 
              />
            </div>
            <div class="input-group">
              <label class="input-label">時間</label>
              <select v-model="form.start_hm" class="form-select time-select" required>
                <option value="" disabled>選擇時間</option>
                <option 
                  v-for="t in timeSlots" 
                  :key="t" 
                  :value="t"
                  :disabled="form.spot_id && form.start_date && isTimeSlotBooked(form.start_date, t, form.spot_id)"
                  :class="{ 'disabled-option': form.spot_id && form.start_date && isTimeSlotBooked(form.start_date, t, form.spot_id) }"
                >
                  {{ t }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="time-group">
          <h4 class="time-title">
            <span class="time-icon">🕐</span>
            預約結束時間
          </h4>
          <div class="time-inputs">
            <div class="input-group">
              <label class="input-label">日期</label>
              <input 
                type="date" 
                v-model="form.end_date" 
                class="form-input date-input"
                :class="{ 'disabled': form.spot_id && form.end_date && isDateFullyBooked(form.end_date, form.spot_id) }"
                required 
              />
            </div>
            <div class="input-group">
              <label class="input-label">時間</label>
              <select v-model="form.end_hm" class="form-select time-select" required>
                <option value="" disabled>選擇時間</option>
                <option 
                  v-for="t in timeSlots" 
                  :key="t" 
                  :value="t"
                  :disabled="form.spot_id && form.end_date && isTimeSlotBooked(form.end_date, t, form.spot_id)"
                  :class="{ 'disabled-option': form.spot_id && form.end_date && isTimeSlotBooked(form.end_date, t, form.spot_id) }"
                >
                  {{ t }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-submit">
          <span class="btn-icon">✨</span>
          送出預約
        </button>
      </div>
    </form>

    <div class="reservations-section">
      <div class="section-header">
        <h3 class="section-title">
          <span class="section-icon">📋</span>
          目前預約狀況
        </h3>
        <p class="section-subtitle">依開始時間排序顯示</p>
      </div>
      
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>車位</th>
              <th>姓名</th>
              <th>戶別</th>
              <th>手機</th>
              <th>開始時間</th>
              <th>結束時間</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reservations" :key="r.id" class="table-row">
              <td class="spot-cell">
                <span class="spot-badge">{{ findSpotNumber(r.spot_id) }}</span>
              </td>
              <td>{{ r.name }}</td>
              <td>{{ r.household }}</td>
              <td>{{ r.phone }}</td>
              <td class="time-cell">{{ formatDate(r.start_time) }}</td>
              <td class="time-cell">{{ formatDate(r.end_time) }}</td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="reservations.length === 0" class="empty-state">
          <div class="empty-icon">📅</div>
          <p class="empty-text">目前沒有任何預約</p>
          <p class="empty-subtext">快來預約您的第一個車位吧！</p>
        </div>
      </div>
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

// 檢查特定日期是否完全被預約
function isDateFullyBooked(date, spotId) {
  if (!date || !spotId) return false
  
  const dayReservations = reservations.value.filter(r => {
    if (r.spot_id !== spotId) return false
    
    const startDate = new Date(r.start_time).toISOString().split('T')[0]
    const endDate = new Date(r.end_time).toISOString().split('T')[0]
    
    return startDate <= date && endDate >= date
  })
  
  if (dayReservations.length === 0) return false
  
  // 檢查是否覆蓋整天（00:00-23:59）
  const sortedReservations = dayReservations.sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  
  // 合併重疊的時間段
  const mergedIntervals = []
  for (const reservation of sortedReservations) {
    const startTime = new Date(reservation.start_time)
    const endTime = new Date(reservation.end_time)
    
    if (mergedIntervals.length === 0) {
      mergedIntervals.push({ start: startTime, end: endTime })
    } else {
      const lastInterval = mergedIntervals[mergedIntervals.length - 1]
      if (startTime <= lastInterval.end) {
        lastInterval.end = new Date(Math.max(lastInterval.end.getTime(), endTime.getTime()))
      } else {
        mergedIntervals.push({ start: startTime, end: endTime })
      }
    }
  }
  
  // 檢查合併後的時間段是否覆蓋整天
  if (mergedIntervals.length === 1) {
    const interval = mergedIntervals[0]
    const dayStart = new Date(date + 'T00:00:00')
    const dayEnd = new Date(date + 'T23:59:59')
    
    return interval.start <= dayStart && interval.end >= dayEnd
  }
  
  return false
}

// 檢查特定時間段是否已被預約
function isTimeSlotBooked(date, time, spotId) {
  if (!date || !time || !spotId) return false
  
  const checkDateTime = new Date(`${date}T${time}:00`)
  
  return reservations.value.some(r => {
    if (r.spot_id !== spotId) return false
    
    const startTime = new Date(r.start_time)
    const endTime = new Date(r.end_time)
    
    return checkDateTime >= startTime && checkDateTime < endTime
  })
}

// 清理禁用時間段的選擇
watch(() => [form.spot_id, form.start_date], ([spotId, startDate]) => {
  if (spotId && startDate && isTimeSlotBooked(startDate, form.start_hm, spotId)) {
    form.start_hm = ''
  }
})

watch(() => [form.spot_id, form.end_date], ([spotId, endDate]) => {
  if (spotId && endDate && isTimeSlotBooked(endDate, form.end_hm, spotId)) {
    form.end_hm = ''
  }
})

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

<style scoped>
.reservation-form {
  max-width: 100%;
}

.form {
  margin-bottom: var(--spacing-2xl);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.form-group {
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-md);
}

.label-text {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  color: var(--color-gray-700);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-sm);
}

.form-input, .form-select {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
  background: var(--color-white);
}

.form-input:focus, .form-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

/* 禁用狀態的視覺樣式 */
.form-input.disabled {
  background-color: var(--color-gray-100);
  color: var(--color-gray-400);
  border-color: var(--color-gray-200);
  cursor: not-allowed;
}

.disabled-option {
  background-color: var(--color-gray-100) !important;
  color: var(--color-gray-400) !important;
  opacity: 0.6;
}

/* select 中禁用選項的樣式 */
select option:disabled {
  background-color: var(--color-gray-100);
  color: var(--color-gray-400);
  opacity: 0.6;
}

.form-input::placeholder {
  color: var(--color-gray-400);
}

.time-section {
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-2xl);
}

.time-group {
  margin-bottom: var(--spacing-xl);
}

.time-group:last-child {
  margin-bottom: 0;
}

.time-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 var(--spacing-lg) 0;
}

.time-icon {
  font-size: var(--font-size-base);
}

.time-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-gray-600);
  margin-bottom: var(--spacing-sm);
}

.date-input, .time-select {
  min-height: 48px;
}

.form-actions {
  display: flex;
  justify-content: center;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-gray-200);
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-lg) var(--spacing-2xl);
  border-radius: var(--radius-md);
  font-size: var(--font-size-lg);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-md);
  min-width: 160px;
  justify-content: center;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-submit:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: var(--font-size-base);
}

.reservations-section {
  margin-top: var(--spacing-2xl);
}

.section-header {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 var(--spacing-sm) 0;
}

.section-icon {
  font-size: var(--font-size-lg);
}

.section-subtitle {
  color: var(--color-gray-600);
  font-size: var(--font-size-sm);
  margin: 0;
}

.table-container {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.table-row {
  transition: background-color var(--transition-fast);
}

.spot-cell {
  text-align: center;
}

.spot-badge {
  display: inline-block;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.time-cell {
  font-family: monospace;
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  background: var(--color-white);
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-lg);
  opacity: 0.5;
}

.empty-text {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-gray-600);
  margin: 0 0 var(--spacing-sm) 0;
}

.empty-subtext {
  font-size: var(--font-size-sm);
  color: var(--color-gray-500);
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .time-inputs {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .time-section {
    padding: var(--spacing-lg);
  }
  
  .btn-submit {
    width: 100%;
    padding: var(--spacing-lg);
  }
  
  .table {
    font-size: var(--font-size-sm);
  }
  
  .table th, .table td {
    padding: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .table-container {
    overflow-x: auto;
  }
  
  .table {
    min-width: 600px;
  }
}
</style>
