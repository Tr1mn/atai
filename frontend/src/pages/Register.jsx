import { useState } from 'react'
import { Link, useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register, user, loading } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', full_name: '', age: '', city: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return null
  if (user) return <Navigate to="/" replace />

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (parseInt(form.age) < 18) { setError('Минимальный возраст — 18 лет'); return }
    setSubmitting(true)
    try {
      await register({ ...form, age: parseInt(form.age) })
      navigate('/profile')
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка регистрации')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="card p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🏔️</div>
          <h1 className="text-2xl font-bold">Создать аккаунт</h1>
          <p className="text-gray-500 text-sm mt-1">Начни путешествовать по Кыргызстану</p>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Полное имя</label>
            <input className="input" required value={form.full_name} onChange={set('full_name')} placeholder="Aizat Mamytova" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Возраст</label>
              <input className="input" type="number" min="18" max="100" required value={form.age} onChange={set('age')} placeholder="25" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Город</label>
              <input className="input" required value={form.city} onChange={set('city')} placeholder="Бишкек" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input className="input" type="email" required value={form.email} onChange={set('email')} placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input className="input" type="password" minLength="6" required value={form.password} onChange={set('password')} placeholder="Минимум 6 символов" />
          </div>
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</div>}
          <button type="submit" disabled={submitting} className="btn-primary w-full py-2.5">
            {submitting ? 'Регистрируем...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Уже есть аккаунт? <Link to="/login" className="text-blue-700 font-medium hover:underline">Войти</Link>
        </p>
      </div>
    </div>
  )
}
