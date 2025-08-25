<template>
  <div class="admin-panel">
    <!-- Login Form -->
    <div v-if="!loggedIn" class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h3 class="login-title">
            <span class="login-icon">🔐</span>
            管理者登入
          </h3>
          <p class="login-subtitle">請輸入您的管理員憑證</p>
        </div>
        
        <form @submit.prevent="login" class="login-form">
          <div class="form-group">
            <label class="form-label">
              <span class="label-text">👤 帳號</span>
              <input 
                v-model="loginForm.username" 
                class="form-input"
                placeholder="請輸入管理員帳號"
                required 
              />
            </label>
          </div>
          
          <div class="form-group">
            <label class="form-label">
              <span class="label-text">🔑 密碼</span>
              <input 
                v-model="loginForm.password" 
                type="password" 
                class="form-input"
                placeholder="請輸入密碼"
                required 
              />
            </label>
          </div>
          
          <button type="submit" class="btn-login">
            <span class="btn-icon">🚀</span>
            登入管理系統
          </button>
        </form>
      </div>
    </div>

    <!-- Admin Dashboard -->
    <div v-else class="admin-dashboard">
      <!-- Header Actions -->
      <div class="dashboard-header">
        <div class="welcome-message">
          <h3 class="welcome-title">
            <span class="welcome-icon">👋</span>
            歡迎回來，管理員
          </h3>
          <p class="welcome-subtitle">系統管理中心</p>
        </div>
        
        <div class="header-actions">
          <button @click="refresh" class="btn-secondary">
            <span class="btn-icon">🔄</span>
            重新整理
          </button>
          <button @click="logout" class="btn-danger">
            <span class="btn-icon">🚪</span>
            登出
          </button>
        </div>
      </div>

      <!-- Parking Spots Management -->
      <section class="management-section">
        <div class="section-header">
          <h3 class="section-title">
            <span class="section-icon">🅿️</span>
            車位管理
          </h3>
          <p class="section-subtitle">新增、編輯和管理停車位</p>
        </div>
        
        <div class="add-spot-form">
          <form @submit.prevent="createSpot" class="spot-form">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">車位號碼</span>
                  <input 
                    v-model="newSpot" 
                    class="form-input"
                    placeholder="例：A-06"
                    required 
                  />
                </label>
              </div>
              
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="newSpotActive" 
                    class="form-checkbox"
                  />
                  <span class="checkbox-text">立即啟用</span>
                </label>
              </div>
              
              <button type="submit" class="btn-success">
                <span class="btn-icon">➕</span>
                新增車位
              </button>
            </div>
          </form>
        </div>
        
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>車位號碼</th>
                <th>狀態</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in spots" :key="s.id" class="table-row">
                <td class="id-cell">{{ s.id }}</td>
                <td class="spot-cell">
                  <input 
                    v-model="s.edit_number" 
                    class="inline-input"
                    :class="{ 'edited': s.edit_number !== s.spot_number }"
                  />
                </td>
                <td class="status-cell">
                  <label class="status-toggle">
                    <input 
                      type="checkbox" 
                      v-model="s.edit_active" 
                      class="status-checkbox"
                    />
                    <span 
                      class="status-badge" 
                      :class="{ 'active': s.edit_active, 'inactive': !s.edit_active }"
                    >
                      {{ s.edit_active ? '啟用' : '停用' }}
                    </span>
                  </label>
                </td>
                <td class="action-cell">
                  <button 
                    @click="updateSpot(s)" 
                    class="btn-update"
                    :class="{ 'has-changes': s.edit_number !== s.spot_number || s.edit_active !== s.active }"
                  >
                    <span class="btn-icon">💾</span>
                    儲存
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="spots.length === 0" class="empty-state">
            <div class="empty-icon">🅿️</div>
            <p class="empty-text">尚無車位資料</p>
            <p class="empty-subtext">請新增第一個車位</p>
          </div>
        </div>
      </section>

      <!-- Reservations Management -->
      <section class="management-section">
        <div class="section-header">
          <h3 class="section-title">
            <span class="section-icon">📋</span>
            預約管理
          </h3>
          <p class="section-subtitle">查看和取消現有預約</p>
        </div>
        
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>車位</th>
                <th>姓名</th>
                <th>戶別</th>
                <th>手機</th>
                <th>開始時間</th>
                <th>結束時間</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in reservations" :key="r.id" class="table-row">
                <td class="id-cell">{{ r.id }}</td>
                <td class="spot-cell">
                  <span class="spot-badge">{{ findSpotNumber(r.spot_id) }}</span>
                </td>
                <td>{{ r.name }}</td>
                <td>{{ r.household }}</td>
                <td class="phone-cell">{{ r.phone }}</td>
                <td class="time-cell">{{ formatDate(r.start_time) }}</td>
                <td class="time-cell">{{ formatDate(r.end_time) }}</td>
                <td class="action-cell">
                  <button 
                    @click="remove(r.id)" 
                    class="btn-remove"
                  >
                    <span class="btn-icon">🗑️</span>
                    取消
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="reservations.length === 0" class="empty-state">
            <div class="empty-icon">📅</div>
            <p class="empty-text">目前沒有預約</p>
            <p class="empty-subtext">所有車位都是空閒的</p>
          </div>
        </div>
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

<style scoped>
.admin-panel {
  max-width: 100%;
}

/* Login Styles */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.login-card {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  width: 100%;
  max-width: 400px;
}

.login-header {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  padding: var(--spacing-2xl);
  text-align: center;
}

.login-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin: 0 0 var(--spacing-sm) 0;
}

.login-icon {
  font-size: var(--font-size-lg);
}

.login-subtitle {
  font-size: var(--font-size-sm);
  opacity: 0.9;
  margin: 0;
}

.login-form {
  padding: var(--spacing-2xl);
}

.btn-login {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-md);
  margin-top: var(--spacing-md);
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Dashboard Styles */
.admin-dashboard {
  max-width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-gray-100) 100%);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-2xl);
  border: 1px solid var(--color-gray-200);
}

.welcome-message {
  flex: 1;
}

.welcome-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 var(--spacing-xs) 0;
}

.welcome-icon {
  font-size: var(--font-size-lg);
}

.welcome-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn-secondary {
  background: linear-gradient(135deg, var(--color-gray-500) 0%, var(--color-gray-600) 100%);
}

.btn-danger {
  background: linear-gradient(135deg, var(--color-danger) 0%, var(--color-danger-dark) 100%);
}

.btn-secondary, .btn-danger {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.btn-secondary:hover, .btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Management Section Styles */
.management-section {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  margin-bottom: var(--spacing-2xl);
  overflow: hidden;
}

.section-header {
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-gray-100) 100%);
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--color-gray-200);
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
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
  margin: 0;
}

/* Form Styles */
.add-spot-form {
  padding: var(--spacing-xl);
  background: var(--color-gray-50);
  border-bottom: 1px solid var(--color-gray-200);
}

.spot-form {
  max-width: 800px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: var(--spacing-lg);
  align-items: end;
}

.form-group {
  position: relative;
}

.checkbox-group {
  display: flex;
  align-items: center;
  padding-top: var(--spacing-lg);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  font-weight: 500;
  color: var(--color-gray-700);
}

.form-checkbox {
  width: auto;
  margin: 0;
  accent-color: var(--color-primary);
}

.checkbox-text {
  font-size: var(--font-size-sm);
}

.btn-success {
  background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-secondary-dark) 100%);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.btn-success:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Table Styles */
.table-container {
  position: relative;
  overflow: hidden;
}

.table-row {
  transition: background-color var(--transition-fast);
}

.id-cell {
  font-weight: 600;
  color: var(--color-gray-500);
  text-align: center;
  width: 80px;
}

.spot-cell {
  position: relative;
}

.inline-input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  background: var(--color-gray-50);
  transition: all var(--transition-fast);
}

.inline-input:focus {
  border-color: var(--color-primary);
  background: var(--color-white);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  outline: none;
}

.inline-input.edited {
  border-color: var(--color-warning);
  background: #fef3c7;
}

.status-cell {
  text-align: center;
}

.status-toggle {
  position: relative;
  cursor: pointer;
}

.status-checkbox {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.status-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.status-badge.active {
  background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-secondary-dark) 100%);
  color: var(--color-white);
}

.status-badge.inactive {
  background: linear-gradient(135deg, var(--color-gray-400) 0%, var(--color-gray-500) 100%);
  color: var(--color-white);
}

.action-cell {
  text-align: center;
  width: 120px;
}

.btn-update {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  justify-content: center;
  min-width: 80px;
}

.btn-update:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-update.has-changes {
  background: linear-gradient(135deg, var(--color-warning) 0%, #d97706 100%);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.btn-remove {
  background: linear-gradient(135deg, var(--color-danger) 0%, var(--color-danger-dark) 100%);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  justify-content: center;
  min-width: 80px;
}

.btn-remove:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
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

.phone-cell {
  font-family: monospace;
  font-size: var(--font-size-sm);
}

.time-cell {
  font-family: monospace;
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
}

/* Empty State */
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
  .dashboard-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .checkbox-group {
    padding-top: 0;
    justify-content: center;
  }
  
  .btn-success {
    justify-content: center;
  }
  
  .table {
    font-size: var(--font-size-sm);
  }
  
  .table th, .table td {
    padding: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .login-card {
    margin: var(--spacing-md);
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .table {
    min-width: 700px;
  }
  
  .dashboard-header {
    margin: var(--spacing-md);
    border-radius: var(--radius-md);
  }
  
  .management-section {
    margin: var(--spacing-md);
    border-radius: var(--radius-md);
  }
}
</style>
