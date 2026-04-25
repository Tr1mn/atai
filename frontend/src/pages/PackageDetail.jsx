import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function PackageDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [pkg, setPkg] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    api.get(`/api/packages/${id}`).then(r => setPkg(r.data)).finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="text-center py-20 text-gray-400">Загружаем...</div>
  if (!pkg) return <div className="text-center py-20 text-gray-400">Тур не найден</div>

  const inclusions = (() => { try { return JSON.parse(pkg.inclusions) } catch { return [] } })()
  const exclusions = (() => { try { return JSON.parse(pkg.exclusions) } catch { return [] } })()
  const itinerary = (() => { try { return JSON.parse(pkg.itinerary) } catch { return [] } })()
  const nearestDate = pkg.dates?.find(d => d.available_slots > 0)

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      {/* Hero */}
      <div className="rounded-2xl overflow-hidden h-72 mb-6 bg-gray-100">
        {pkg.photo_url && (
          <img src={pkg.photo_url} alt={pkg.title} className="w-full h-full object-cover" />
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2">
          <div className="flex gap-2 mb-3">
            {pkg.featured && <span className="badge bg-yellow-100 text-yellow-800">⭐ Топ</span>}
            <span className="badge-blue">{pkg.duration_days} дн.</span>
            <span className="badge bg-gray-100 text-gray-700">📍 {pkg.destination}</span>
          </div>
          <h1 className="text-3xl font-bold mb-2">{pkg.title}</h1>
          <p className="text-gray-500 mb-6">{pkg.description}</p>

          {/* Tabs */}
          <div className="flex gap-1 mb-6 border-b">
            {[['overview', 'Обзор'], ['itinerary', 'Маршрут'], ['policy', 'Условия']].map(([key, label]) => (
              <button key={key} onClick={() => setActiveTab(key)}
                className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition ${activeTab === key ? 'border-blue-700 text-blue-700' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
                {label}
              </button>
            ))}
          </div>

          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="card p-4">
                  <div className="text-xs text-gray-500 mb-1">Размер группы</div>
                  <div className="font-semibold">👥 {pkg.min_group_size} — {pkg.max_group_size} чел.</div>
                </div>
                <div className="card p-4">
                  <div className="text-xs text-gray-500 mb-1">Сложность</div>
                  <div className="font-semibold">{{ easy: '🟢 Лёгкий', moderate: '🟡 Средний', hard: '🔴 Сложный' }[pkg.difficulty]}</div>
                </div>
              </div>
              {inclusions.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">✅ Включено</h3>
                  <ul className="space-y-1">{inclusions.map((i, idx) => <li key={idx} className="text-sm text-gray-600 flex gap-2"><span className="text-green-500">•</span>{i}</li>)}</ul>
                </div>
              )}
              {exclusions.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">❌ Не включено</h3>
                  <ul className="space-y-1">{exclusions.map((i, idx) => <li key={idx} className="text-sm text-gray-600 flex gap-2"><span className="text-red-400">•</span>{i}</li>)}</ul>
                </div>
              )}
            </div>
          )}

          {activeTab === 'itinerary' && (
            <div className="space-y-4">
              {itinerary.map((day) => (
                <div key={day.day} className="flex gap-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-700 text-white flex items-center justify-center font-bold text-sm">{day.day}</div>
                  <div className="card p-4 flex-1">
                    <h4 className="font-semibold mb-1">{day.title}</h4>
                    <p className="text-sm text-gray-500">{day.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'policy' && (
            <div className="card p-6 space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Политика отмены</h3>
                <p className="text-sm text-gray-600">{pkg.cancellation_policy || 'Уточните у партнера'}</p>
              </div>
              {pkg.family_rates_enabled && (
                <div className="bg-pink-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-pink-800 mb-1">👨‍👩‍👧 Семейная скидка</h3>
                  <p className="text-sm text-pink-700">2–3 человека: скидка 20% · 4 и более: скидка 30%</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Booking sidebar */}
        <div className="lg:col-span-1">
          <div className="card p-6 sticky top-20">
            <div className="text-3xl font-bold text-blue-700 mb-1">{pkg.price.toLocaleString()} $</div>
            <div className="text-sm text-gray-500 mb-4">за человека</div>

            {pkg.dates?.length > 0 ? (
              <div className="space-y-2 mb-4">
                <div className="text-sm font-medium text-gray-700">Ближайшие даты:</div>
                {pkg.dates.slice(0, 3).map(d => (
                  <div key={d.id} className="flex justify-between items-center text-sm py-2 border-b border-gray-100">
                    <span>{new Date(d.start_date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                    <span className={d.available_slots === 0 ? 'text-red-500' : 'text-green-600'}>
                      {d.available_slots === 0 ? 'Нет мест' : `${d.available_slots} мест`}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-gray-400 mb-4">Даты не указаны</div>
            )}

            {user ? (
              nearestDate ? (
                <Link to={`/packages/${pkg.id}/book`} className="btn-primary w-full text-center block py-3">
                  Забронировать
                </Link>
              ) : (
                <button className="btn-secondary w-full py-3" disabled>Нет доступных мест</button>
              )
            ) : (
              <Link to="/login" className="btn-primary w-full text-center block py-3">Войти для брони</Link>
            )}

            <div className="mt-4 text-xs text-gray-400 text-center">🔒 Безопасное бронирование · Возврат по условиям</div>
          </div>
        </div>
      </div>
    </div>
  )
}
