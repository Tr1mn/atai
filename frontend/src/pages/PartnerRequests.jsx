import { useEffect, useState } from 'react'
import api from '../api/client'
import { travelLabel, travelLabels } from '../utils/travelLabels'

const emptyOffer = {
  title: '',
  description: '',
  price_total: '',
  price_per_person: '',
  duration_days: '',
  included: 'Трансфер, гид, организация маршрута',
  message: '',
}

export default function PartnerRequests() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [offers, setOffers] = useState({})
  const [submittingOfferId, setSubmittingOfferId] = useState(null)
  const [offerErrors, setOfferErrors] = useState({})
  const [pageError, setPageError] = useState('')

  const load = () => {
    setLoading(true)
    setPageError('')
    return api.get('/api/travel-requests/open')
      .then((res) => {
        setRequests(res.data)
        return res.data
      })
      .catch((err) => {
        setRequests([])
        const status = err.response?.status
        if (status === 403) {
          setPageError('Ваш партнёрский аккаунт ещё не активен. Дождитесь одобрения администратора, чтобы отправлять предложения.')
        } else {
          setPageError('Не удалось загрузить заявки туристов. Проверьте подключение к backend.')
        }
        return []
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const setOffer = (requestId, key, value) => {
    setOffers((prev) => ({
      ...prev,
      [requestId]: { ...(prev[requestId] || emptyOffer), [key]: value },
    }))
    setOfferErrors((prev) => ({ ...prev, [requestId]: '' }))
  }

  const validateOffer = (form) => {
    const priceTotal = parseFloat(form.price_total)
    const pricePerPerson = form.price_per_person ? parseFloat(form.price_per_person) : null
    const durationDays = form.duration_days ? parseInt(form.duration_days, 10) : null

    if (!form.title.trim()) return 'Укажите название предложения.'
    if (!Number.isFinite(priceTotal) || priceTotal <= 0) return 'Укажите общую цену больше 0.'
    if (pricePerPerson !== null && (!Number.isFinite(pricePerPerson) || pricePerPerson <= 0)) {
      return 'Цена за человека должна быть больше 0.'
    }
    if (durationDays !== null && (!Number.isFinite(durationDays) || durationDays < 1)) {
      return 'Количество дней должно быть не меньше 1.'
    }
    return ''
  }

  const submitOffer = async (requestId) => {
    const form = offers[requestId] || emptyOffer
    const validationError = validateOffer(form)
    if (validationError) {
      setOfferErrors((prev) => ({ ...prev, [requestId]: validationError }))
      return
    }

    setSubmittingOfferId(requestId)
    setOfferErrors((prev) => ({ ...prev, [requestId]: '' }))

    try {
      await api.post(`/api/travel-requests/${requestId}/offers`, {
        title: form.title.trim(),
        description: form.description.trim(),
        price_total: parseFloat(form.price_total),
        price_per_person: form.price_per_person ? parseFloat(form.price_per_person) : null,
        duration_days: form.duration_days ? parseInt(form.duration_days, 10) : null,
        included: form.included.trim(),
        message: form.message.trim(),
      })
      setOffers((prev) => ({ ...prev, [requestId]: emptyOffer }))
      await load()
    } catch (err) {
      const status = err.response?.status
      const detail = err.response?.data?.detail
      let message = 'Не удалось отправить предложение. Проверьте цену и обязательные поля.'

      if (status === 403) {
        message = 'Ваш партнёрский аккаунт ещё не активен. Дождитесь одобрения администратора.'
      } else if (status === 400 && typeof detail === 'string' && detail.includes('already')) {
        message = 'Вы уже отправили предложение для этой заявки. Обновляем список...'
        await load()
      } else if (typeof detail === 'string') {
        message = detail
      }

      setOfferErrors((prev) => ({ ...prev, [requestId]: message }))
    } finally {
      setSubmittingOfferId(null)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Заявки туристов</h1>
        <p className="text-gray-500">
          Туристы заполняют анкету, а вы можете предложить подходящий маршрут, пакет и выгодную цену.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-400">Загружаем заявки...</div>
      ) : pageError ? (
        <div className="card p-8 text-center text-red-600 bg-red-50 border-red-100">{pageError}</div>
      ) : requests.length === 0 ? (
        <div className="card p-8 text-center text-gray-500">Открытых заявок пока нет</div>
      ) : (
        <div className="space-y-5">
          {requests.map((request) => {
            const existingOffer = request.offers[0]
            const form = offers[request.id] || emptyOffer
            const isSubmitting = submittingOfferId === request.id
            const error = offerErrors[request.id]
            return (
              <div key={request.id} className="card p-5">
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="badge-blue">Новая заявка</span>
                      <span className="text-xs text-gray-400">{new Date(request.created_at).toLocaleDateString('ru-RU')}</span>
                    </div>
                    <h2 className="font-semibold text-xl mb-2">{request.user_name}: {request.origin} · {travelLabel(request.days)}</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600 mb-4">
                      <div>Компания: {travelLabel(request.companions)}</div>
                      <div>Бюджет: {travelLabel(request.budget)}</div>
                      <div>Сезон: {travelLabel(request.season)}</div>
                      <div>Сложность: {travelLabel(request.difficulty)}</div>
                      <div>Формат: {travelLabel(request.travel_format)}</div>
                      <div>Главное: {travelLabel(request.priority)}</div>
                    </div>

                    <div className="space-y-3">
                      <TagBlock title="Интересы" items={travelLabels(request.interests)} />
                      <TagBlock title="Активности" items={travelLabels(request.activities)} />
                      <TagBlock title="Места" items={travelLabels(request.preferred_places)} />
                    </div>

                    {request.notes && <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 mt-4">{request.notes}</p>}
                  </div>

                  <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    {existingOffer ? (
                      <div>
                        <h3 className="font-semibold mb-2">Вы уже отправили предложение</h3>
                        <p className="text-sm text-gray-600 mb-3">{existingOffer.title}</p>
                        <div className="font-bold text-blue-700">{existingOffer.price_total.toLocaleString()} $</div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <h3 className="font-semibold">Предложить пакет</h3>
                        <input className="input text-sm" placeholder="Название предложения" value={form.title} onChange={(e) => setOffer(request.id, 'title', e.target.value)} />
                        <textarea className="input h-20 resize-none text-sm" placeholder="Коротко опишите маршрут" value={form.description} onChange={(e) => setOffer(request.id, 'description', e.target.value)} />
                        <div className="grid grid-cols-2 gap-2">
                          <input className="input text-sm" type="number" placeholder="Цена всего $" value={form.price_total} onChange={(e) => setOffer(request.id, 'price_total', e.target.value)} />
                          <input className="input text-sm" type="number" placeholder="$/чел." value={form.price_per_person} onChange={(e) => setOffer(request.id, 'price_per_person', e.target.value)} />
                        </div>
                        <input className="input text-sm" type="number" placeholder="Дней" value={form.duration_days} onChange={(e) => setOffer(request.id, 'duration_days', e.target.value)} />
                        <input className="input text-sm" placeholder="Что включено" value={form.included} onChange={(e) => setOffer(request.id, 'included', e.target.value)} />
                        <textarea className="input h-16 resize-none text-sm" placeholder="Сообщение туристу" value={form.message} onChange={(e) => setOffer(request.id, 'message', e.target.value)} />
                        {error && <div className="text-sm text-red-700 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</div>}
                        <button
                          onClick={() => submitOffer(request.id)}
                          disabled={isSubmitting || !form.title.trim() || !form.price_total}
                          className="btn-primary w-full py-2 text-sm"
                        >
                          {isSubmitting ? 'Отправляем...' : 'Отправить предложение'}
                        </button>
                      </div>
                    )}
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

function TagBlock({ title, items }) {
  if (!items.length) return null
  return (
    <div>
      <div className="text-xs font-medium text-gray-500 mb-1">{title}</div>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => <span key={item} className="badge bg-white text-gray-700 border border-gray-200">{item}</span>)}
      </div>
    </div>
  )
}
