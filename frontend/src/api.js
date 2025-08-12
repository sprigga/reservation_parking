import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const api = axios.create({ baseURL })

// Attach Authorization header if token exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('rp_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
