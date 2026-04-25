import { useEffect, useState } from 'react'
import api from '../api/client'

const statusConfig = {
  pending_payment: { label: 'Ожидает оплаты', cls: 'badge-yellow' },
  paid: { label: 'Оплачено', cls: 'badge-blue' },
  pending_confirmation: { label: 'На подтверждении', cls: 'badge-yellow' },
  confirmed: { label: 'Подтверждено', cls: 'badge-green' },
  completed: { label: 'Завершено', cls: 'badge bg-gray-100 text-gray-700' },
  cancelled_by_user: { label: 'Отменено вами', cls: 'badge-red' },
  cancelled_by_partner: { label: 'Отменено партнером', cls: 'badge-red' },
  expired: { label: 'Истекло', cls: 'badge-red' },
}

export default function MyBookings() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(null)

  const load = () => {
    setLoading(true)
    api.get('/api/bookings/me').then(r => setBookings(r.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const cancel = async (id) => {
    if (!confirm('Отменить бронь? Возврат согласно политике.')) return
    setCancelling(id)
    try {
      await api.post(`/api/bookings/${id}/cancel`)
      load()
    } finally {
      setCancelling(null)
    }
  }

  const pay = async (id) => {
    await api.post(`/api/bookings/${id}/pay`)
    load()
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Мои бронирования</h1>
      {loading ? (
        <div className="text-center py-20 text-gray-400">Загружаем...</div>
      ) : bookings.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📋</div>
          <p className="text-gray-500 mb-4">У вас нет бронирований</p>
          <a href="/packages" className="btn-primary px-6 py-2.5">Смотреть туры</a>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map(b => {
            const s = statusConfig[b.status] || { label: b.status, cls: 'badge-yellow' }
            return (
              <div key={b.id} className="card p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold">Бронь #{b.id}</span>
                      <span className={s.cls}>{s.label}</span>
                    </div>
                    <div className="text-sm text-gray-500 space-y-1">
                      <div>Тур #{b.package_id} · {b.num_travelers} чел.</div>
                      <div>Создано: {new Date(b.created_at).toLocaleDateString('ru-RU')}</div>
                      {b.expires_at && b.status === 'pending_payment' && (
                        <div className="text-orange-600">Оплатить до: {new Date(b.expires_at).toLocaleString('ru-RU')}</div>
                      )}
                      {b.family_discount_pct > 0 && <div className="text-green-600">Скидка {b.family_discount_pct}%</div>}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-blue-700">{b.total_price.toLocaleString()} $</div>
                    <div className="flex gap-2 mt-2 justify-end">
                      {b.status === 'pending_payment' && (
                        <button onClick={() => pay(b.id)} className="btn-primary text-sm py-1.5 px-3">Оплатить</button>
                      )}
                      {['pending_payment', 'paid', 'confirmed'].includes(b.status) && (
                        <button onClick={() => cancel(b.id)} disabled={cancelling === b.id} className="btn-danger text-sm py-1.5 px-3">
                          {cancelling === b.id ? '...' : 'Отменить'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
