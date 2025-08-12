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

// Auto logout on 401 and reload to show login form
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status
    if (status === 401) {
      try { localStorage.removeItem('rp_token') } catch {}
      // Optionally show a brief notice
      // alert('登入已過期，請重新登入')
      if (typeof window !== 'undefined' && window.location) {
        window.location.reload()
      }
    }
    return Promise.reject(error)
  }
)

export default api
