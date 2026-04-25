import { useEffect, useState } from 'react'
import api from '../api/client'

export default function PartnerDashboard() {
  const [tab, setTab] = useState('stats')
  const [stats, setStats] = useState(null)
  const [packages, setPackages] = useState([])
  const [bookings, setBookings] = useState([])
  const [form, setForm] = useState({ title: '', description: '', destination: '', region: '', price: '', duration_days: '', min_group_size: 2, max_group_size: 12, inclusions: '["Проживание","Питание","Гид"]', exclusions: '["Авиабилеты","Личные расходы"]', cancellation_policy: 'Полный возврат > 14 дней. 50% за 7-14 дней. 0% менее 7 дней.', itinerary: '[]', photo_url: '', difficulty: 'easy', travel_style: 'mixed', family_friendly: true, family_rates_enabled: false, dates: [] })
  const [adding, setAdding] = useState(false)
  const [dateInput, setDateInput] = useState({ start_date: '', total_slots: 10 })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))

  useEffect(() => {
    api.get('/api/partners/me/stats').then(r => setStats(r.data)).catch(() => {})
    api.get('/api/partners/me/packages').then(r => setPackages(r.data)).catch(() => {})
    api.get('/api/partners/me/bookings').then(r => setBookings(r.data)).catch(() => {})
  }, [])

  const addDate = () => {
    if (!dateInput.start_date) return
    setForm(f => ({ ...f, dates: [...f.dates, { start_date: new Date(dateInput.start_date).toISOString(), total_slots: parseInt(dateInput.total_slots) }] }))
    setDateInput({ start_date: '', total_slots: 10 })
  }

  const createPackage = async (e) => {
    e.preventDefault()
    setAdding(true)
    try {
      await api.post('/api/packages/', { ...form, price: parseFloat(form.price), duration_days: parseInt(form.duration_days), min_group_size: parseInt(form.min_group_size), max_group_size: parseInt(form.max_group_size) })
      api.get('/api/partners/me/packages').then(r => setPackages(r.data))
      setTab('packages')
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка')
    } finally {
      setAdding(false)
    }
  }

  const statusBadge = { pending_payment: 'badge-yellow', paid: 'badge-blue', confirmed: 'badge-green', completed: 'badge bg-gray-100 text-gray-700', cancelled_by_user: 'badge-red', expired: 'badge-red' }
  const pkgStatus = { draft: 'badge-yellow', under_moderation: 'badge-yellow', published: 'badge-green', archived: 'badge bg-gray-100 text-gray-700', rejected: 'badge-red' }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Кабинет партнера</h1>
      <div className="flex gap-2 mb-8 flex-wrap">
        {[['stats', 'Аналитика'], ['packages', 'Туры'], ['bookings', 'Брони'], ['add', '+ Добавить тур']].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} className={`btn ${tab === key ? 'btn-primary' : 'btn-secondary'}`}>{label}</button>
        ))}
      </div>

      {tab === 'stats' && stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            ['Туры', stats.total_packages, '📦'],
            ['Брони', stats.total_bookings, '📋'],
            ['Подтверждено', stats.confirmed_bookings, '✅'],
            ['GMV', `${stats.gmv.toLocaleString()} $`, '💰'],
            ['Комиссия платформы', `${stats.commission_owed.toLocaleString()} $`, '📊'],
            ['Выплата вам', `${stats.payout.toLocaleString()} $`, '💳'],
          ].map(([label, val, icon]) => (
            <div key={label} className="card p-4 text-center">
              <div className="text-2xl mb-1">{icon}</div>
              <div className="text-xl font-bold">{val}</div>
              <div className="text-xs text-gray-500">{label}</div>
            </div>
          ))}
        </div>
      )}

      {tab === 'packages' && (
        <div className="space-y-3">
          {packages.length === 0 ? <div className="text-gray-400 text-center py-10">Нет туров. Добавьте первый!</div> :
            packages.map(p => (
              <div key={p.id} className="card p-4 flex gap-4 items-center">
                <img src={p.photo_url || 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=100'} className="w-16 h-16 object-cover rounded-lg flex-shrink-0" />
                <div className="flex-1">
                  <div className="flex gap-2 mb-1">
                    <span className={pkgStatus[p.status] || 'badge-yellow'}>{p.status}</span>
                    {p.featured && <span className="badge bg-yellow-100 text-yellow-800">⭐ Featured</span>}
                  </div>
                  <div className="font-semibold">{p.title}</div>
                  <div className="text-sm text-gray-500">{p.destination} · {p.duration_days} дн. · {p.price.toLocaleString()} $</div>
                </div>
              </div>
            ))
          }
        </div>
      )}

      {tab === 'bookings' && (
        <div className="space-y-3">
          {bookings.length === 0 ? <div className="text-gray-400 text-center py-10">Броней пока нет</div> :
            bookings.map(b => (
              <div key={b.id} className="card p-4 flex justify-between items-center">
                <div>
                  <div className="flex gap-2 mb-1"><span className={statusBadge[b.status] || 'badge-yellow'}>{b.status}</span></div>
                  <div className="text-sm text-gray-500">Бронь #{b.id} · {b.num_travelers} чел. · {new Date(b.created_at).toLocaleDateString('ru-RU')}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-blue-700">{b.total_price.toLocaleString()} $</div>
                  {b.status === 'paid' && (
                    <button onClick={() => api.post(`/api/bookings/${b.id}/confirm`).then(() => api.get('/api/partners/me/bookings').then(r => setBookings(r.data)))}
                      className="btn-primary text-xs py-1 px-2 mt-1">Подтвердить</button>
                  )}
                </div>
              </div>
            ))
          }
        </div>
      )}

      {tab === 'add' && (
        <div className="card p-6 max-w-2xl">
          <h2 className="font-semibold text-lg mb-6">Новый тур</h2>
          <form onSubmit={createPackage} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">Название тура</label><input className="input" required value={form.title} onChange={set('title')} /></div>
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">Описание</label><textarea className="input h-20 resize-none" value={form.description} onChange={set('description')} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Направление</label><input className="input" required value={form.destination} onChange={set('destination')} placeholder="Иссык-Куль" /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Регион</label><input className="input" value={form.region} onChange={set('region')} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Цена ($/чел.)</label><input className="input" type="number" required value={form.price} onChange={set('price')} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Длительность (дн.)</label><input className="input" type="number" required value={form.duration_days} onChange={set('duration_days')} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Мин. группа</label><input className="input" type="number" value={form.min_group_size} onChange={set('min_group_size')} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Макс. группа</label><input className="input" type="number" value={form.max_group_size} onChange={set('max_group_size')} /></div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Сложность</label>
                <select className="input" value={form.difficulty} onChange={set('difficulty')}><option value="easy">Лёгкий</option><option value="moderate">Средний</option><option value="hard">Сложный</option></select>
              </div>
              <div><label className="block text-sm font-medium text-gray-700 mb-1">Стиль</label>
                <select className="input" value={form.travel_style} onChange={set('travel_style')}><option value="adventure">Приключения</option><option value="relax">Отдых</option><option value="culture">Культура</option><option value="mixed">Смешанный</option></select>
              </div>
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">URL фото</label><input className="input" value={form.photo_url} onChange={set('photo_url')} placeholder="https://..." /></div>
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">Включено (JSON массив)</label><input className="input" value={form.inclusions} onChange={set('inclusions')} /></div>
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">Не включено (JSON массив)</label><input className="input" value={form.exclusions} onChange={set('exclusions')} /></div>
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">Политика отмены *</label><textarea className="input h-16 resize-none" required value={form.cancellation_policy} onChange={set('cancellation_policy')} /></div>
              <div className="col-span-2 flex gap-4">
                <label className="flex items-center gap-2 text-sm cursor-pointer"><input type="checkbox" checked={form.family_friendly} onChange={set('family_friendly')} /> Семейный</label>
                <label className="flex items-center gap-2 text-sm cursor-pointer"><input type="checkbox" checked={form.family_rates_enabled} onChange={set('family_rates_enabled')} /> Семейные тарифы</label>
              </div>
            </div>

            {/* Dates */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Даты отправления</label>
              <div className="flex gap-2 mb-2">
                <input className="input flex-1" type="date" value={dateInput.start_date} onChange={e => setDateInput(d => ({ ...d, start_date: e.target.value }))} />
                <input className="input w-24" type="number" placeholder="Мест" value={dateInput.total_slots} onChange={e => setDateInput(d => ({ ...d, total_slots: e.target.value }))} />
                <button type="button" onClick={addDate} className="btn-secondary px-3">+</button>
              </div>
              {form.dates.map((d, i) => (
                <div key={i} className="text-sm text-gray-600 bg-gray-50 px-3 py-1 rounded mb-1">
                  {new Date(d.start_date).toLocaleDateString('ru-RU')} · {d.total_slots} мест
                </div>
              ))}
            </div>

            <button type="submit" disabled={adding} className="btn-primary w-full py-2.5">
              {adding ? 'Отправляем на модерацию...' : 'Создать тур'}
            </button>
            <p className="text-xs text-gray-400 text-center">Тур будет опубликован после проверки модератором</p>
          </form>
        </div>
      )}
    </div>
  )
}
