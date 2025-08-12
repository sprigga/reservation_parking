<template>
  <div>
    <div v-if="!loggedIn" style="margin-bottom: 16px; padding: 12px; border: 1px solid #ddd;">
      <h3>管理者登入</h3>
      <form @submit.prevent="login">
        <label>帳號 <input v-model="loginForm.username" required /></label>
        <label>密碼 <input v-model="loginForm.password" type="password" required /></label>
        <div><button type="submit">登入</button></div>
      </form>
    </div>

    <div v-else>
      <div style="margin-bottom: 12px; display:flex; gap:8px; align-items:center;">
        <button @click="refresh">重新整理</button>
        <button @click="logout">登出</button>
      </div>

      <section style="margin-bottom: 24px;">
        <h3>車位管理</h3>
        <form @submit.prevent="createSpot" style="margin-bottom:12px;">
          <label>車位號碼 <input v-model="newSpot" required /></label>
          <label style="margin-left: 8px;">啟用 <input type="checkbox" v-model="newSpotActive" /></label>
          <button type="submit" style="margin-left: 8px;">新增</button>
        </form>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>號碼</th>
              <th>啟用</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in spots" :key="s.id">
              <td>{{ s.id }}</td>
              <td>
                <input v-model="s.edit_number" />
              </td>
              <td>
                <input type="checkbox" v-model="s.edit_active" />
              </td>
              <td>
                <button @click="updateSpot(s)">儲存</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <h3>預約管理</h3>
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
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'
import { setToken, clearToken, isLoggedIn } from '../auth'

const reservations = ref([])
const spots = ref([])

const loggedIn = ref(isLoggedIn())
const loginForm = ref({ username: '', password: '' })

const newSpot = ref('')
const newSpotActive = ref(true)

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
    api.get('/spots', { params: { include_inactive: true } }),
  ])
  reservations.value = r1.data
  spots.value = r2.data.map(s => ({ ...s, edit_number: s.spot_number, edit_active: s.active }))
}

async function login() {
  try {
    const params = new URLSearchParams()
    params.append('username', loginForm.value.username)
    params.append('password', loginForm.value.password)
    const { data } = await api.post('/auth/login', params)
    setToken(data.access_token)
    loggedIn.value = true
    await refresh()
  } catch (err) {
    alert(err?.response?.data?.detail || err.message)
  }
}

function logout() {
  clearToken()
  loggedIn.value = false
}

async function createSpot() {
  try {
    const payload = { spot_number: newSpot.value, active: newSpotActive.value }
    await api.post('/spots', payload)
    newSpot.value = ''
    newSpotActive.value = true
    await refresh()
  } catch (err) {
    alert(err?.response?.data?.detail || err.message)
  }
}

async function updateSpot(s) {
  try {
    const payload = { spot_number: s.edit_number, active: s.edit_active }
    await api.patch(`/spots/${s.id}`, payload)
    await refresh()
  } catch (err) {
    alert(err?.response?.data?.detail || err.message)
  }
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
