import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function Booking() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [pkg, setPkg] = useState(null)
  const [pkgLoading, setPkgLoading] = useState(true)
  const [pkgError, setPkgError] = useState(false)

  const [form, setForm] = useState({
    num_travelers: 1,
    is_family_booking: false,
    package_date_id: '',
  })
  const [formErrors, setFormErrors] = useState({})
  const [booking, setBooking] = useState(null)
  const [loading, setLoading] = useState(false)
  const [paying, setPaying] = useState(false)
  const [error, setError] = useState('')

  // Always fetch from the API — page must work on direct URL and after refresh.
  useEffect(() => {
    api.get(`/api/packages/${id}`)
      .then(r => {
        setPkg(r.data)
        const nearest = r.data.dates?.find(d => d.available_slots > 0)
        if (nearest) setForm(f => ({ ...f, package_date_id: nearest.id }))
      })
      .catch(() => setPkgError(true))
      .finally(() => setPkgLoading(false))
  }, [id])

  if (pkgLoading) return <div className="text-center py-20 text-gray-400">Загружаем тур...</div>
  if (pkgError || !pkg) return (
    <div className="text-center py-20">
      <p className="text-gray-400 mb-4">Тур не найден.</p>
      <a href="/packages" className="text-blue-700 underline">Назад к турам</a>
    </div>
  )

  const availableDates = pkg.dates?.filter(d => d.available_slots > 0) ?? []
  const discount = form.is_family_booking
    ? (form.num_travelers >= 4 ? 30 : form.num_travelers >= 2 ? 20 : 0)
    : 0
  const base = pkg.price * form.num_travelers
  const total = base * (1 - discount / 100)

  const validate = () => {
    const errs = {}
    if (!form.package_date_id) errs.package_date_id = 'Выберите дату'
    if (!form.num_travelers || form.num_travelers < 1) errs.num_travelers = 'Минимум 1 путешественник'
    if (form.num_travelers > pkg.max_group_size)
      errs.num_travelers = `Максимум ${pkg.max_group_size} чел. для этого тура`
    return errs
  }

  const createBooking = async () => {
    setError('')
    const errs = validate()
    if (Object.keys(errs).length) { setFormErrors(errs); return }
    setFormErrors({})
    setLoading(true)
    try {
      const { data } = await api.post('/api/bookings/', {
        package_id: parseInt(id),
        package_date_id: parseInt(form.package_date_id),
        num_travelers: form.num_travelers,
        is_family_booking: form.is_family_booking,
      })
      setBooking(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка бронирования')
      // Refresh availability so the date selector reflects current slot counts
      api.get(`/api/packages/${id}`).then(r => setPkg(r.data)).catch(() => {})
    } finally {
      setLoading(false)
    }
  }

  const mockPay = async () => {
    setPaying(true)
    try {
      const { data } = await api.post(`/api/bookings/${booking.id}/pay`)
      setBooking(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка оплаты')
    } finally {
      setPaying(false)
    }
  }

  if (booking?.status === 'paid') {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold mb-2">Бронь оформлена!</h1>
        <p className="text-gray-500 mb-2">Номер брони: <strong>#{booking.id}</strong></p>
        <p className="text-gray-500 mb-6">Итого оплачено: <strong>{booking.total_price.toLocaleString()} $</strong></p>
        <p className="text-sm text-blue-700 mb-6">Партнер подтвердит бронь в течение 48 часов</p>
        <button onClick={() => navigate('/my-bookings')} className="btn-primary px-6 py-2.5">Мои брони</button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Оформление брони</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="card p-6 space-y-5">
          <h2 className="font-semibold text-lg">Детали поездки</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Дата начала</label>
            {availableDates.length === 0 ? (
              <p className="text-sm text-red-600">Нет доступных дат. <a href={`/packages/${id}`} className="underline">Вернуться к туру</a></p>
            ) : (
              <select
                className={`input ${formErrors.package_date_id ? 'border-red-500' : ''}`}
                value={form.package_date_id}
                onChange={e => setForm(f => ({ ...f, package_date_id: e.target.value }))}
              >
                <option value="">— Выберите дату —</option>
                {availableDates.map(d => (
                  <option key={d.id} value={d.id}>
                    {new Date(d.start_date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })} ({d.available_slots} мест)
                  </option>
                ))}
              </select>
            )}
            {formErrors.package_date_id && <p className="text-xs text-red-600 mt-1">{formErrors.package_date_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Количество путешественников</label>
            <input
              className={`input ${formErrors.num_travelers ? 'border-red-500' : ''}`}
              type="number" min="1" max={pkg.max_group_size}
              value={form.num_travelers}
              onChange={e => setForm(f => ({ ...f, num_travelers: parseInt(e.target.value) || 1 }))}
            />
            {formErrors.num_travelers
              ? <p className="text-xs text-red-600 mt-1">{formErrors.num_travelers}</p>
              : <p className="text-xs text-gray-400 mt-1">Макс. {pkg.max_group_size} чел.</p>
            }
          </div>

          {pkg.family_rates_enabled && (
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" checked={form.is_family_booking}
                onChange={e => setForm(f => ({ ...f, is_family_booking: e.target.checked }))}
                className="w-4 h-4 text-blue-700 rounded" />
              <div>
                <div className="text-sm font-medium">Семейное бронирование</div>
                <div className="text-xs text-gray-500">Скидка 20% (2–3 чел.) или 30% (4+ чел.)</div>
              </div>
            </label>
          )}

          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</div>}

          {!booking ? (
            <button
              onClick={createBooking}
              disabled={loading || availableDates.length === 0}
              className="btn-primary w-full py-3"
            >
              {loading ? 'Создаём бронь...' : 'Создать бронь'}
            </button>
          ) : (
            <div className="space-y-3">
              <div className="bg-green-50 text-green-800 p-3 rounded-lg text-sm">
                ✅ Бронь #{booking.id} создана. У вас 24 часа для оплаты.
              </div>
              <button onClick={mockPay} disabled={paying} className="btn-primary w-full py-3">
                {paying ? 'Обрабатываем...' : '💳 Оплатить (тестовый режим)'}
              </button>
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="card p-6">
          <h2 className="font-semibold text-lg mb-4">Итоговая сумма</h2>
          <img src={pkg.photo_url} alt={pkg.title} className="w-full h-36 object-cover rounded-lg mb-4" />
          <h3 className="font-semibold mb-4">{pkg.title}</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Цена за чел.</span><span>{pkg.price.toLocaleString()} $</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Кол-во</span><span>× {form.num_travelers}</span></div>
            {discount > 0 && <div className="flex justify-between text-green-600"><span>Семейная скидка</span><span>−{discount}%</span></div>}
            <div className="border-t pt-2 flex justify-between font-bold text-lg">
              <span>Итого</span><span className="text-blue-700">{total.toLocaleString()} $</span>
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg text-xs text-blue-800">
            🔒 Бронь защищена политикой возврата платформы Atai Travel
          </div>
        </div>
      </div>
    </div>
  )
}
