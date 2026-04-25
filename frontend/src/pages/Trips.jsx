import { useEffect, useState } from 'react'
import api from '../api/client'
import TripCard from '../components/TripCard'

export default function Trips() {
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('browse')
  const [form, setForm] = useState({ title: '', destination: '', description: '', start_date: '', end_date: '', min_size: 2, max_size: 8, budget_min: 0, budget_max: 50000, travel_style: 'mixed', photo_url: '' })
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    api.get('/api/trips/').then(r => setTrips(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const create = async (e) => {
    e.preventDefault()
    setError('')
    setCreating(true)
    try {
      await api.post('/api/trips/', { ...form, min_size: parseInt(form.min_size), max_size: parseInt(form.max_size), budget_min: parseFloat(form.budget_min), budget_max: parseFloat(form.budget_max) })
      setTab('browse')
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Поездки</h1>
          <p className="text-gray-500 text-sm">Найди компанию или создай свою поездку</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setTab('browse')} className={`btn ${tab === 'browse' ? 'btn-primary' : 'btn-secondary'}`}>Все поездки</button>
          <button onClick={() => setTab('create')} className={`btn ${tab === 'create' ? 'btn-primary' : 'btn-secondary'}`}>+ Создать</button>
        </div>
      </div>

      {tab === 'browse' && (
        loading ? (
          <div className="text-center py-20 text-gray-400">Загружаем...</div>
        ) : trips.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">🗺️</div>
            <p className="text-gray-500 mb-4">Поездок пока нет — создай первую!</p>
            <button onClick={() => setTab('create')} className="btn-primary px-6 py-2.5">Создать поездку</button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trips.map(t => <TripCard key={t.id} trip={t} />)}
          </div>
        )
      )}

      {tab === 'create' && (
        <div className="card p-6 max-w-xl">
          <h2 className="font-semibold text-lg mb-6">Создать поездку</h2>
          <form onSubmit={create} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
              <input className="input" required value={form.title} onChange={set('title')} placeholder="Ищу попутчиков на Иссык-Куль!" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Направление</label>
              <input className="input" required value={form.destination} onChange={set('destination')} placeholder="Иссык-Куль" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
              <textarea className="input h-20 resize-none" value={form.description} onChange={set('description')} placeholder="Расскажи о поездке..." />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Дата начала</label>
                <input className="input" type="date" required value={form.start_date} onChange={set('start_date')} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Дата конца</label>
                <input className="input" type="date" required value={form.end_date} onChange={set('end_date')} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Мин. группа</label>
                <input className="input" type="number" min="2" value={form.min_size} onChange={set('min_size')} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Макс. группа</label>
                <input className="input" type="number" min="2" value={form.max_size} onChange={set('max_size')} />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Стиль</label>
              <select className="input" value={form.travel_style} onChange={set('travel_style')}>
                <option value="adventure">Приключения</option>
                <option value="relax">Отдых</option>
                <option value="culture">Культура</option>
                <option value="mixed">Смешанный</option>
              </select>
            </div>
            {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</div>}
            <button type="submit" disabled={creating} className="btn-primary w-full py-2.5">
              {creating ? 'Создаём...' : 'Создать поездку'}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
