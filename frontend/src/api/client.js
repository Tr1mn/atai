import axios from 'axios'

const api = axios.create({
  // Empty baseURL → requests go to the same origin as the frontend.
  // In dev, Vite proxies /api/* → http://127.0.0.1:8001 (see vite.config.js).
  // In production, set VITE_API_URL if the API lives on a different domain.
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
})

// No request interceptor needed — the browser attaches the cookie automatically.

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // /api/auth/me returns 401 for unauthenticated users — that is expected and
    // handled by AuthContext. Redirecting on it would cause an infinite reload loop.
    const url = err.config?.url ?? ''
    if (err.response?.status === 401 && !url.includes('/api/auth/me')) {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
