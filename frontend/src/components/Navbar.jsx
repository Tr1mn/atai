import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useEffect, useState } from 'react'
import api from '../api/client'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [incomingLikeCount, setIncomingLikeCount] = useState(0)

  useEffect(() => {
    if (!user || user.role !== 'tourist') {
      setIncomingLikeCount(0)
      return
    }
    api.get('/api/users/me/incoming-likes')
      .then(r => setIncomingLikeCount(r.data.length))
      .catch(() => setIncomingLikeCount(0))
  }, [user])

  const handleLogout = () => { logout(); navigate('/') }

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-blue-700">
            <span className="text-2xl">🏔️</span> Atai Travel
          </Link>

          <div className="hidden md:flex items-center gap-4 lg:gap-6 text-sm font-medium text-gray-600">
            <Link to="/packages" className="hover:text-blue-700 transition">Туры</Link>
            <Link
              to="/ai-assistant"
              className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-2 font-semibold text-blue-700 shadow-sm transition hover:border-blue-300 hover:bg-blue-100"
            >
              AI ассистент
            </Link>
            {user && <Link to="/travel-request" className="hover:text-blue-700 transition">Подбор тура</Link>}
            {user && <Link to="/trips" className="hover:text-blue-700 transition">Попутчики</Link>}
            {user && (
              <Link to="/individual" className="hover:text-blue-700 transition relative">
                Индивидуальный
                {incomingLikeCount > 0 && (
                  <span className="ml-1 inline-flex min-w-[18px] h-[18px] items-center justify-center rounded-full bg-red-500 px-1 text-[11px] leading-none text-white">
                    {incomingLikeCount}
                  </span>
                )}
              </Link>
            )}
            {user && <Link to="/matching" className="hover:text-blue-700 transition">Matching</Link>}
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/ai-assistant"
              className="md:hidden inline-flex h-9 min-w-9 items-center justify-center rounded-full border border-blue-200 bg-blue-50 px-3 text-sm font-semibold text-blue-700 hover:bg-blue-100"
              aria-label="AI ассистент"
            >
              <span className="hidden sm:inline">AI ассистент</span>
              <span className="sm:hidden">AI</span>
            </Link>
            {user ? (
              <div className="relative">
                <button onClick={() => setOpen(!open)} className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-blue-700">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">
                    {user.full_name?.[0]}
                  </div>
                  <span className="hidden md:inline">{user.full_name}</span>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                </button>
                {open && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50">
                    <Link to="/ai-assistant" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">AI ассистент</Link>
                    <Link to="/profile" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Мой профиль</Link>
                    <Link to="/my-bookings" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Мои брони</Link>
                    <Link to="/my-requests" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Мои заявки</Link>
                    <Link to="/individual" onClick={() => setOpen(false)} className="flex items-center justify-between px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                      <span>Индивидуальный</span>
                      {incomingLikeCount > 0 && <span className="badge-red">{incomingLikeCount}</span>}
                    </Link>
                    {user.role === 'partner' && <Link to="/partner" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Кабинет партнера</Link>}
                    {user.role === 'partner' && <Link to="/partner/requests" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Заявки туристов</Link>}
                    {user.role === 'admin' && <Link to="/admin" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Админ панель</Link>}
                    {user.role === 'tourist' && <Link to="/become-partner" onClick={() => setOpen(false)} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Стать партнером</Link>}
                    <hr className="my-1" />
                    <button onClick={() => { setOpen(false); handleLogout() }} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Выйти</button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-blue-700">Войти</Link>
                <Link to="/register" className="btn-primary text-sm">Регистрация</Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
