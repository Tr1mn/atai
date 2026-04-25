import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // loading = true while the initial /me request is in flight.
  // PrivateRoute waits for this before deciding to redirect.
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    api.get('/api/auth/me', { signal: controller.signal })
      .then(r => setUser(r.data))
      .catch(err => {
        // CanceledError means StrictMode cleanup aborted the first request — ignore it
        if (err.name !== 'CanceledError') setUser(null)
      })
      .finally(() => {
        // Only mark loading done for the real request, not the StrictMode-aborted one
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await api.post('/api/auth/login', { email, password })
    // Token is in the HTTP-only cookie. Store only non-sensitive fields for UI.
    const { user_id, role, full_name } = data
    setUser({ user_id, role, full_name })
    return data
  }, [])

  const register = useCallback(async (form) => {
    const { data } = await api.post('/api/auth/register', form)
    const { user_id, role, full_name } = data
    setUser({ user_id, role, full_name })
    return data
  }, [])

  const logout = useCallback(async () => {
    await api.post('/api/auth/logout').catch(() => {})
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
