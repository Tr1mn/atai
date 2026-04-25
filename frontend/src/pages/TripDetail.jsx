import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

const statusConfig = {
  open: { label: 'Набор открыт', cls: 'badge-green' },
  group_formed: { label: 'Группа собрана', cls: 'badge-blue' },
  active: { label: 'В поездке', cls: 'badge-yellow' },
  completed: { label: 'Завершена', cls: 'badge bg-gray-100 text-gray-700' },
  cancelled: { label: 'Отменена', cls: 'badge-red' },
}

export default function TripDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [trip, setTrip] = useState(null)
  const [loading, setLoading] = useState(true)
  const [joining, setJoining] = useState(false)
  const [msg, setMsg] = useState('')

  const load = () => {
    setLoading(true)
    api.get(`/api/trips/${id}`).then(r => setTrip(r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [id])

  const join = async () => {
    setJoining(true)
    try {
      await api.post(`/api/trips/${id}/join`)
      setMsg('Заявка отправлена организатору!')
      load()
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Ошибка')
    } finally {
      setJoining(false)
    }
  }

  const acceptMember = async (userId) => {
    await api.post(`/api/trips/${id}/members/${userId}/accept`)
    load()
  }

  if (loading) return <div className="text-center py-20 text-gray-400">Загружаем...</div>
  if (!trip) return <div className="text-center py-20">Поездка не найдена</div>

  const s = statusConfig[trip.status] || { label: trip.status, cls: 'badge-yellow' }
  const isMember = trip.members?.some(m => m.user_id === user?.id && m.status === 'accepted')
  const isOrganizer = trip.organizer_id === user?.id
  const hasPending = trip.members?.some(m => m.user_id === user?.id && m.status === 'pending')
  const pendingMembers = trip.members?.filter(m => m.status === 'pending' && m.user_id !== trip.organizer_id)
  const acceptedMembers = trip.members?.filter(m => m.status === 'accepted')

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="h-56 rounded-2xl overflow-hidden mb-6">
        <img src={trip.photo_url || 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800'} alt={trip.title} className="w-full h-full object-cover" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex gap-2 mb-3"><span className={s.cls}>{s.label}</span></div>
          <h1 className="text-2xl font-bold mb-2">{trip.title}</h1>
          <p className="text-gray-500 mb-6">{trip.description}</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              ['📍', 'Направление', trip.destination],
              ['📅', 'Начало', new Date(trip.start_date).toLocaleDateString('ru-RU')],
              ['👥', 'Группа', `${trip.current_size}/${trip.max_size}`],
              ['💰', 'Бюджет', `${trip.budget_min.toLocaleString()} – ${trip.budget_max.toLocaleString()} $`],
            ].map(([icon, label, val]) => (
              <div key={label} className="card p-3 text-center">
                <div className="text-xl mb-1">{icon}</div>
                <div className="text-xs text-gray-500 mb-0.5">{label}</div>
                <div className="text-sm font-semibold">{val}</div>
              </div>
            ))}
          </div>

          {/* Members */}
          <div>
            <h3 className="font-semibold mb-3">Участники ({acceptedMembers?.length})</h3>
            <div className="flex gap-2 flex-wrap">
              {acceptedMembers?.map(m => (
                <div key={m.id} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5 text-sm">
                  <div className="w-6 h-6 rounded-full bg-blue-200 flex items-center justify-center text-xs font-bold text-blue-700">
                    {m.user_id === trip.organizer_id ? '👑' : '👤'}
                  </div>
                  <span>{m.user_id === trip.organizer_id ? 'Организатор' : `Участник #${m.user_id}`}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Pending approvals (organizer only) */}
          {isOrganizer && pendingMembers?.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">Заявки ({pendingMembers.length})</h3>
              <div className="space-y-2">
                {pendingMembers.map(m => (
                  <div key={m.id} className="card p-3 flex items-center justify-between">
                    <span className="text-sm">Пользователь #{m.user_id}</span>
                    <button onClick={() => acceptMember(m.user_id)} className="btn-primary text-sm py-1 px-3">Принять</button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div>
          <div className="card p-5">
            <div className="text-sm text-gray-500 mb-4">
              Мест осталось: <span className="font-bold text-gray-900">{trip.max_size - trip.current_size}</span>
            </div>
            {msg && <div className="text-sm text-blue-700 bg-blue-50 px-3 py-2 rounded-lg mb-3">{msg}</div>}
            {!isOrganizer && !isMember && !hasPending && trip.status === 'open' && (
              <button onClick={join} disabled={joining} className="btn-primary w-full py-2.5">
                {joining ? 'Отправляем...' : 'Присоединиться'}
              </button>
            )}
            {hasPending && <div className="text-sm text-yellow-700 bg-yellow-50 px-3 py-2 rounded-lg">Ваша заявка рассматривается</div>}
            {isMember && <div className="text-sm text-green-700 bg-green-50 px-3 py-2 rounded-lg">✓ Вы участник этой поездки</div>}
            {isOrganizer && <div className="text-sm text-blue-700 bg-blue-50 px-3 py-2 rounded-lg">👑 Вы организатор</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
