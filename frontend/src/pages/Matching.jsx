import { useEffect, useState } from 'react'
import api from '../api/client'

export default function Matching() {
  const [users, setUsers] = useState([])
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('browse')
  const [likeStatus, setLikeStatus] = useState({})

  useEffect(() => {
    api.get('/api/users/').then(r => setUsers(r.data)).catch(() => {}).finally(() => setLoading(false))
    api.get('/api/users/me/matches').then(r => setMatches(r.data)).catch(() => {})
  }, [])

  const like = async (userId) => {
    setLikeStatus(s => ({ ...s, [userId]: 'loading' }))
    try {
      const { data } = await api.post(`/api/users/${userId}/like`)
      setLikeStatus(s => ({ ...s, [userId]: data.matched ? 'matched' : 'liked' }))
      if (data.matched) {
        api.get('/api/users/me/matches').then(r => setMatches(r.data)).catch(() => {})
      }
      setUsers(prev => prev.filter(u => u.id !== userId))
    } catch {
      setLikeStatus(s => ({ ...s, [userId]: 'error' }))
    }
  }

  const styleLabel = { adventure: '🧗 Приключения', relax: '🏖️ Отдых', culture: '🏛️ Культура', mixed: '🌍 Смешанный' }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-2">Найти попутчиков</h1>
      <p className="text-gray-500 mb-6">Лайкай профили — взаимный лайк открывает чат</p>

      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('browse')} className={`btn ${tab === 'browse' ? 'btn-primary' : 'btn-secondary'}`}>Поиск</button>
        <button onClick={() => setTab('matches')} className={`btn ${tab === 'matches' ? 'btn-primary' : 'btn-secondary'} relative`}>
          Matches
          {matches.length > 0 && <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-1.5">{matches.length}</span>}
        </button>
      </div>

      {tab === 'browse' && (
        loading ? (
          <div className="text-center py-20 text-gray-400">Загружаем профили...</div>
        ) : users.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">🎉</div>
            <p className="text-gray-500">Вы просмотрели все доступные профили</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {users.map(u => (
              <div key={u.id} className="card overflow-hidden">
                <div className="relative">
                  <img src={u.photo_url || `https://i.pravatar.cc/150?u=${u.id}`} alt={u.full_name} className="w-full h-48 object-cover" />
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 p-3 text-white">
                    <div className="font-bold">{u.full_name}, {u.age}</div>
                    <div className="text-sm opacity-80">📍 {u.city}</div>
                  </div>
                </div>
                <div className="p-4">
                  {u.bio && <p className="text-sm text-gray-600 mb-3 line-clamp-2">{u.bio}</p>}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {u.travel_style && <span className="badge-blue text-xs">{styleLabel[u.travel_style] || u.travel_style}</span>}
                    {u.interests?.split(',').filter(Boolean).slice(0, 2).map(i => (
                      <span key={i} className="badge bg-gray-100 text-gray-600 text-xs">{i.trim()}</span>
                    ))}
                  </div>
                  <button
                    onClick={() => like(u.id)}
                    disabled={likeStatus[u.id] === 'loading' || likeStatus[u.id] === 'liked' || likeStatus[u.id] === 'matched'}
                    className={`w-full py-2 rounded-lg font-medium text-sm transition ${
                      likeStatus[u.id] === 'matched' ? 'bg-green-100 text-green-700' :
                      likeStatus[u.id] === 'liked' ? 'bg-blue-100 text-blue-700' :
                      'btn-primary'
                    }`}
                  >
                    {likeStatus[u.id] === 'matched' ? '🎉 Match!' : likeStatus[u.id] === 'liked' ? '✓ Лайкнуто' : likeStatus[u.id] === 'loading' ? '...' : '❤️ Лайк'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      )}

      {tab === 'matches' && (
        matches.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">💫</div>
            <p className="text-gray-500">Пока нет взаимных лайков — продолжай знакомиться!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {matches.map(m => (
              <div key={m.match_id} className="card p-4 flex items-center gap-4">
                <img src={m.user.photo_url || `https://i.pravatar.cc/80?u=${m.user.id}`} alt={m.user.full_name} className="w-14 h-14 rounded-full object-cover" />
                <div className="flex-1">
                  <div className="font-semibold">{m.user.full_name}</div>
                  <div className="text-sm text-gray-500">📍 {m.user.city}</div>
                  <div className="text-xs text-gray-400">Match {new Date(m.created_at).toLocaleDateString('ru-RU')}</div>
                </div>
                <div className="text-green-500 text-2xl">💚</div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  )
}
