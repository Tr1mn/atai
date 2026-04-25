import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { travelLabel } from '../utils/travelLabels'

const statusLabel = {
  open: ['badge-blue', 'Открыта'],
  matched: ['badge-green', 'Предложение принято'],
  closed: ['badge bg-gray-100 text-gray-700', 'Закрыта'],
}

export default function MyTravelRequests() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/api/travel-requests/me')
      .then((res) => setRequests(res.data))
      .catch(() => setRequests([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const acceptOffer = async (offerId) => {
    await api.put(`/api/travel-requests/offers/${offerId}/accept`)
    load()
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Мои заявки на тур</h1>
          <p className="text-gray-500">Здесь появляются предложения от турагентств по вашей анкете.</p>
        </div>
        <Link to="/travel-request" className="btn-primary text-center">Заполнить новую анкету</Link>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-400">Загружаем заявки...</div>
      ) : requests.length === 0 ? (
        <div className="card p-8 text-center">
          <h2 className="font-semibold text-lg mb-2">У вас пока нет заявок</h2>
          <p className="text-gray-500 mb-5">Заполните анкету, и партнеры смогут предложить маршрут и цену.</p>
          <Link to="/travel-request" className="btn-primary">Заполнить анкету</Link>
        </div>
      ) : (
        <div className="space-y-5">
          {requests.map((request) => {
            const [badgeClass, label] = statusLabel[request.status] || statusLabel.open
            return (
              <div key={request.id} className="card p-5">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-4">
                  <div>
                    <span className={badgeClass}>{label}</span>
                    <h2 className="font-semibold text-xl mt-2">{request.origin} · {request.days} дней</h2>
                    <p className="text-sm text-gray-500">
                      {travelLabel(request.companions)} · {travelLabel(request.budget)} · {travelLabel(request.season)} · {travelLabel(request.difficulty)}
                    </p>
                  </div>
                  <div className="text-sm text-gray-400">{new Date(request.created_at).toLocaleDateString('ru-RU')}</div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  {request.preferred_places.slice(0, 8).map((place) => (
                    <span key={place} className="badge bg-blue-50 text-blue-800">{travelLabel(place)}</span>
                  ))}
                </div>

                {request.notes && <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 mb-4">{request.notes}</p>}

                <h3 className="font-semibold mb-3">Предложения турагентств</h3>
                {request.offers.length === 0 ? (
                  <div className="text-sm text-gray-400">Пока нет предложений. Партнеры увидят вашу заявку и смогут ответить.</div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                    {request.offers.map((offer) => (
                      <div key={offer.id} className="border border-gray-200 rounded-lg p-4 bg-white">
                        <div className="flex justify-between gap-3 mb-2">
                          <div>
                            <div className="font-semibold">{offer.title}</div>
                            <div className="text-xs text-gray-500">{offer.partner_company}</div>
                          </div>
                          <span className={offer.status === 'accepted' ? 'badge-green' : 'badge-yellow'}>
                            {offer.status === 'accepted' ? 'Принято' : 'Новое'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{offer.description}</p>
                        <div className="text-sm text-gray-500 mb-3">
                          {offer.duration_days && <span>{offer.duration_days} дн. · </span>}
                          <strong className="text-blue-700">{offer.price_total.toLocaleString()} $</strong>
                          {offer.price_per_person && <span> · {offer.price_per_person.toLocaleString()} $/чел.</span>}
                        </div>
                        {offer.included && <div className="text-xs text-gray-500 mb-3">Включено: {offer.included}</div>}
                        {offer.message && <div className="text-xs bg-blue-50 text-blue-800 rounded-lg p-2 mb-3">{offer.message}</div>}
                        {request.status === 'open' && offer.status === 'submitted' && (
                          <button onClick={() => acceptOffer(offer.id)} className="btn-primary w-full py-2 text-sm">Принять предложение</button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
