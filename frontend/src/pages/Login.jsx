import { useState } from 'react'
import { Link, useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login, user, loading } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return null
  if (user) return <Navigate to="/" replace />

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(form.email, form.password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Неверные данные')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="card p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🏔️</div>
          <h1 className="text-2xl font-bold">Войти в Atai Travel</h1>
          <p className="text-gray-500 text-sm mt-1">Добро пожаловать обратно!</p>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input className="input" type="email" required value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input className="input" type="password" required value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} placeholder="••••••••" />
          </div>
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</div>}
          <button type="submit" disabled={submitting} className="btn-primary w-full py-2.5">
            {submitting ? 'Входим...' : 'Войти'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Нет аккаунта? <Link to="/register" className="text-blue-700 font-medium hover:underline">Зарегистрироваться</Link>
        </p>
        <div className="mt-4 p-3 bg-blue-50 rounded-lg text-xs text-blue-800">
          <strong>Demo:</strong> admin@atai.kg / admin123 · partner@nomad.kg / partner123 · aizat@mail.kg / user123
        </div>
      </div>
    </div>
  )
}
