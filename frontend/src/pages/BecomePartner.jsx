import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function BecomePartner() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ company_name: '', legal_info: '', partner_type: 'agency' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post('/api/partners/apply', form)
      // Update local user role
      const stored = JSON.parse(localStorage.getItem('user') || '{}')
      stored.role = 'partner'
      localStorage.setItem('user', JSON.stringify(stored))
      navigate('/partner')
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-2">Стать партнером</h1>
      <p className="text-gray-500 mb-8">Размещай туры на платформе и получай клиентов. Комиссия: 12% с подтвержденных броней.</p>
      <div className="card p-6">
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Название компании</label>
            <input className="input" required value={form.company_name} onChange={set('company_name')} placeholder="ООО Nomad Tours" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Тип партнера</label>
            <select className="input" value={form.partner_type} onChange={set('partner_type')}>
              <option value="agency">Туристическое агентство</option>
              <option value="hotel">Отель / Гостевой дом</option>
              <option value="transport">Транспортная компания</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Юридические данные</label>
            <textarea className="input h-24 resize-none" required value={form.legal_info} onChange={set('legal_info')} placeholder="Регистрационные данные, ИНН, контактное лицо..." />
          </div>
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</div>}
          <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
            {loading ? 'Отправляем...' : 'Подать заявку'}
          </button>
        </form>
      </div>
    </div>
  )
}
