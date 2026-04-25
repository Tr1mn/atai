import { useState, useEffect } from 'react'
import api from '../api/client'

export default function Individual() {
  const [tab, setTab] = useState('new')
  const [candidates, setCandidates] = useState([])
  const [incomingLikes, setIncomingLikes] = useState([])
  const [index, setIndex] = useState(0)
  const [match, setMatch] = useState(null)
  const [loading, setLoading] = useState(true)
  const [incomingLoading, setIncomingLoading] = useState(true)
  const [incomingError, setIncomingError] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadCandidates()
    loadIncomingLikes()
  }, [])

  const current = candidates[index] ?? null

  function loadCandidates() {
    setLoading(true)
    api.get('/api/users/individual')
      .then(r => {
        setCandidates(r.data)
        setIndex(0)
      })
      .catch(() => setCandidates([]))
      .finally(() => setLoading(false))
  }

  function loadIncomingLikes() {
    setIncomingLoading(true)
    setIncomingError('')
    api.get('/api/users/me/incoming-likes')
      .then(r => setIncomingLikes(r.data))
      .catch(() => {
        setIncomingLikes([])
        setIncomingError('Не удалось загрузить входящие лайки')
      })
      .finally(() => setIncomingLoading(false))
  }

  async function openMatch(matchId, fallbackUser) {
    try {
      const { data } = await api.get('/api/users/me/matches')
      const found = data.find(item => item.match_id === matchId)
      setMatch(found || { match_id: matchId, user: fallbackUser })
    } catch {
      setMatch({ match_id: matchId, user: fallbackUser })
    }
  }

  async function likeUser(user, { fromIncoming = false } = {}) {
    if (!user || actionLoading) return
    setActionLoading(true)
    try {
      const { data } = await api.post(`/api/users/${user.id}/like`)
      if (fromIncoming) {
        setIncomingLikes(prev => prev.filter(item => item.user.id !== user.id))
      } else {
        setIndex(i => i + 1)
      }
      if (data.matched) {
        await openMatch(data.match_id, user)
      }
    } catch {
      if (fromIncoming) {
        setIncomingError('Не удалось ответить взаимностью. Попробуйте ещё раз.')
      } else {
        setIndex(i => i + 1)
      }
    } finally {
      setActionLoading(false)
    }
  }

  async function skipUser(user, { fromIncoming = false } = {}) {
    if (!user || actionLoading) return
    setActionLoading(true)
    try {
      await api.post(`/api/users/${user.id}/skip`)
    } catch {
      // Duplicate skips are safe to ignore; the next card can still be shown.
    } finally {
      if (fromIncoming) {
        setIncomingLikes(prev => prev.filter(item => item.user.id !== user.id))
      } else {
        setIndex(i => i + 1)
      }
      setActionLoading(false)
    }
  }

  function dismissMatch() {
    setMatch(null)
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-2 text-center">Индивидуальный подбор</h1>
      <p className="text-gray-500 text-center mb-6">Находите попутчиков по интересам и открывайте контакты после взаимной симпатии</p>

      <div className="flex justify-center gap-2 mb-8">
        <button onClick={() => setTab('new')} className={`btn ${tab === 'new' ? 'btn-primary' : 'btn-secondary'}`}>
          Новые участники
        </button>
        <button onClick={() => setTab('incoming')} className={`btn ${tab === 'incoming' ? 'btn-primary' : 'btn-secondary'} relative`}>
          Вы понравились
          {incomingLikes.length > 0 && (
            <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-1.5">{incomingLikes.length}</span>
          )}
        </button>
      </div>

      {match && <MatchModal match={match} onClose={dismissMatch} />}

      {tab === 'new' && (
        <div className="max-w-md mx-auto">
          {loading ? (
            <div className="flex items-center justify-center min-h-[60vh]">
              <div className="text-gray-500">Загрузка...</div>
            </div>
          ) : !current ? (
            <EmptyState title="Новых анкет пока нет" text="Загляните позже — появятся новые попутчики" />
          ) : (
            <UserCard
              user={current}
              onSkip={() => skipUser(current)}
              onLike={() => likeUser(current)}
              actionLoading={actionLoading}
              likeLabel="Нравится"
              skipLabel="Пропустить"
            />
          )}

          {candidates.length > 0 && index < candidates.length && (
            <p className="text-center text-gray-400 text-xs mt-4">
              {index + 1} / {candidates.length}
            </p>
          )}
        </div>
      )}

      {tab === 'incoming' && (
        <div className="max-w-3xl mx-auto">
          {incomingLoading ? (
            <div className="text-center py-20 text-gray-400">Загружаем входящие лайки...</div>
          ) : incomingError ? (
            <div className="card p-8 text-center text-red-600 bg-red-50 border-red-100">{incomingError}</div>
          ) : incomingLikes.length === 0 ? (
            <EmptyState title="Пока нет новых лайков" text="Когда вы кому-то понравитесь, карточка появится здесь" />
          ) : (
            <div className="space-y-5">
              {incomingLikes.map(item => (
                <div key={item.like_id} className="card p-4 md:p-5">
                  <div className="mb-3">
                    <span className="badge-blue">Вы понравились этому участнику</span>
                  </div>
                  <UserCard
                    user={item.user}
                    compact
                    onSkip={() => skipUser(item.user, { fromIncoming: true })}
                    onLike={() => likeUser(item.user, { fromIncoming: true })}
                    actionLoading={actionLoading}
                    likeLabel="Ответить взаимностью"
                    skipLabel="Пропустить"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function UserCard({ user, onSkip, onLike, actionLoading, likeLabel, skipLabel, compact = false }) {
  return (
    <div className={compact ? 'bg-white rounded-xl overflow-hidden' : 'bg-white rounded-2xl shadow-md overflow-hidden'}>
      <div className={compact ? 'h-56 bg-gray-100' : 'h-72 bg-gray-100'}>
        {user.photo_url ? (
          <img src={user.photo_url} alt={user.full_name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300">
            <svg className="w-24 h-24" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
            </svg>
          </div>
        )}
      </div>

      <div className={compact ? 'pt-4' : 'p-6'}>
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-gray-900">{user.full_name}</h2>
          {user.age && <span className="text-gray-500 text-sm">{user.age} лет</span>}
        </div>
        {user.city && <p className="text-blue-700 text-sm mb-3">📍 {user.city}</p>}
        {user.bio && <p className="text-gray-600 text-sm mb-4 line-clamp-3">{user.bio}</p>}

        <div className="flex flex-wrap gap-2 mb-4">
          {user.travel_style && <span className="badge-blue">{styleLabel(user.travel_style)}</span>}
          {user.interests?.split(',').slice(0, 4).map(i => i.trim()).filter(Boolean).map(tag => (
            <span key={tag} className="badge bg-gray-100 text-gray-600">{tag}</span>
          ))}
          {user.languages && <span className="badge bg-green-50 text-green-700">{user.languages}</span>}
          {(user.budget_min || user.budget_max) && (
            <span className="badge bg-yellow-50 text-yellow-700">
              {Number(user.budget_min || 0).toLocaleString()}–{Number(user.budget_max || 0).toLocaleString()} сом
            </span>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={onSkip}
            disabled={actionLoading}
            className="flex-1 btn-secondary py-3 disabled:opacity-50"
          >
            {skipLabel}
          </button>
          <button
            onClick={onLike}
            disabled={actionLoading}
            className="flex-1 btn-primary py-3 disabled:opacity-50"
          >
            {actionLoading ? '...' : likeLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

function MatchModal({ match, onClose }) {
  const user = match.user
  const hasContacts = user.phone || user.telegram || user.whatsapp || user.instagram

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-sm w-full text-center">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Взаимная симпатия!</h2>
        <p className="text-gray-600 mb-4">
          Вы и <span className="font-semibold">{user.full_name}</span> понравились друг другу. Теперь можно открыть контакты.
        </p>
        <div className="text-left bg-gray-50 rounded-xl p-4 mb-6 space-y-1 text-sm">
          {user.phone && <p><span className="text-gray-500">Телефон:</span> {user.phone}</p>}
          {user.telegram && <p><span className="text-gray-500">Telegram:</span> {user.telegram}</p>}
          {user.whatsapp && <p><span className="text-gray-500">WhatsApp:</span> {user.whatsapp}</p>}
          {user.instagram && <p><span className="text-gray-500">Instagram:</span> {user.instagram}</p>}
          {!hasContacts && <p className="text-gray-400 italic">Пользователь пока не добавил контакты</p>}
        </div>
        <button onClick={onClose} className="btn-primary w-full py-2">
          Продолжить
        </button>
      </div>
    </div>
  )
}

function EmptyState({ title, text }) {
  return (
    <div className="text-center py-20 text-gray-500">
      <div className="text-6xl mb-4">✨</div>
      <p className="text-lg font-medium">{title}</p>
      <p className="text-sm mt-2">{text}</p>
    </div>
  )
}

function styleLabel(style) {
  const labels = {
    adventure: 'Приключения',
    relax: 'Спокойный отдых',
    culture: 'Культура',
    mixed: 'Смешанный стиль',
  }
  return labels[style] || style
}
