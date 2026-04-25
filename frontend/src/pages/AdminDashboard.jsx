import { useEffect, useState } from 'react'
import api from '../api/client'

export default function AdminDashboard() {
  const [tab, setTab] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [partners, setPartners] = useState([])
  const [pendingPkgs, setPendingPkgs] = useState([])
  const [complaints, setComplaints] = useState([])

  useEffect(() => {
    api.get('/api/admin/dashboard').then(r => setStats(r.data)).catch(() => {})
    api.get('/api/admin/users').then(r => setUsers(r.data)).catch(() => {})
    api.get('/api/admin/partners').then(r => setPartners(r.data)).catch(() => {})
    api.get('/api/admin/packages/pending').then(r => setPendingPkgs(r.data)).catch(() => {})
    api.get('/api/admin/complaints').then(r => setComplaints(r.data)).catch(() => {})
  }, [])

  const approvePartner = async (id) => { await api.put(`/api/admin/partners/${id}/approve`); api.get('/api/admin/partners').then(r => setPartners(r.data)) }
  const approvePkg = async (id) => { await api.put(`/api/admin/packages/${id}/approve`); api.get('/api/admin/packages/pending').then(r => setPendingPkgs(r.data)) }
  const rejectPkg = async (id) => { await api.put(`/api/admin/packages/${id}/reject?reason=Не+соответствует+требованиям`); api.get('/api/admin/packages/pending').then(r => setPendingPkgs(r.data)) }
  const setUserStatus = async (id, status) => { await api.put(`/api/admin/users/${id}/status?status=${status}`); api.get('/api/admin/users').then(r => setUsers(r.data)) }
  const resolveComplaint = async (id, action) => { await api.put(`/api/admin/complaints/${id}/resolve?action=${action}`); api.get('/api/admin/complaints').then(r => setComplaints(r.data)) }

  const tabs = [
    ['dashboard', 'Обзор'],
    ['partners', `Партнеры (${partners.filter(p => p.status === 'pending').length} ожидают)`],
    ['packages', `Туры (${pendingPkgs.length} ожидают)`],
    ['users', 'Пользователи'],
    ['complaints', `Жалобы (${complaints.length})`],
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Панель администратора</h1>
      <div className="flex gap-2 mb-8 flex-wrap">
        {tabs.map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} className={`btn text-sm ${tab === key ? 'btn-primary' : 'btn-secondary'}`}>{label}</button>
        ))}
      </div>

      {tab === 'dashboard' && stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            ['Пользователи', stats.total_users, '👥'],
            ['Партнеры', stats.total_partners, '🏢'],
            ['Туры', stats.total_packages, '📦'],
            ['Брони', stats.total_bookings, '📋'],
            ['GMV', `${stats.gmv?.toLocaleString()} $`, '💰'],
            ['Комиссия', `${stats.platform_commission?.toLocaleString()} $`, '📊'],
            ['Жалобы', stats.pending_complaints, '🚨'],
            ['На модерации', stats.pending_packages, '⏳'],
          ].map(([label, val, icon]) => (
            <div key={label} className="card p-4 text-center">
              <div className="text-2xl mb-1">{icon}</div>
              <div className="text-xl font-bold">{val}</div>
              <div className="text-xs text-gray-500">{label}</div>
            </div>
          ))}
        </div>
      )}

      {tab === 'partners' && (
        <div className="space-y-3">
          {partners.map(p => (
            <div key={p.id} className="card p-4 flex items-center justify-between">
              <div>
                <div className="flex gap-2 mb-1">
                  <span className={p.status === 'active' ? 'badge-green' : p.status === 'pending' ? 'badge-yellow' : 'badge-red'}>{p.status}</span>
                  <span className="badge bg-gray-100 text-gray-600">{p.partner_type}</span>
                </div>
                <div className="font-semibold">{p.company_name}</div>
                <div className="text-xs text-gray-500">Комиссия: {p.commission_rate}%</div>
              </div>
              {p.status === 'pending' && (
                <button onClick={() => approvePartner(p.id)} className="btn-primary text-sm py-1.5 px-4">Одобрить</button>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === 'packages' && (
        <div className="space-y-3">
          {pendingPkgs.length === 0 ? <div className="text-gray-400 text-center py-10">Нет туров на модерации</div> :
            pendingPkgs.map(p => (
              <div key={p.id} className="card p-4 flex items-center justify-between">
                <div>
                  <div className="font-semibold">{p.title}</div>
                  <div className="text-sm text-gray-500">{p.destination} · {p.price?.toLocaleString()} $</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => approvePkg(p.id)} className="btn-primary text-sm py-1.5 px-3">✓ Опубликовать</button>
                  <button onClick={() => rejectPkg(p.id)} className="btn-danger text-sm py-1.5 px-3">✗ Отклонить</button>
                </div>
              </div>
            ))
          }
        </div>
      )}

      {tab === 'users' && (
        <div className="space-y-2">
          {users.map(u => (
            <div key={u.id} className="card p-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm">{u.full_name?.[0]}</div>
                <div>
                  <div className="text-sm font-medium">{u.full_name}</div>
                  <div className="text-xs text-gray-500">{u.city} · {u.role}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`badge text-xs ${u.status === 'active' ? 'badge-green' : u.status === 'verified' ? 'badge-blue' : u.status === 'blocked' ? 'badge-red' : 'badge-yellow'}`}>{u.status}</span>
                {u.status !== 'blocked' && u.role !== 'admin' && (
                  <button onClick={() => setUserStatus(u.id, 'blocked')} className="text-xs text-red-600 hover:underline">Блок</button>
                )}
                {u.status === 'blocked' && (
                  <button onClick={() => setUserStatus(u.id, 'active')} className="text-xs text-green-600 hover:underline">Разблок</button>
                )}
                {u.status === 'active' && (
                  <button onClick={() => setUserStatus(u.id, 'verified')} className="text-xs text-blue-600 hover:underline">Верифиц.</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'complaints' && (
        <div className="space-y-3">
          {complaints.length === 0 ? <div className="text-gray-400 text-center py-10">Жалоб нет</div> :
            complaints.map(c => (
              <div key={c.id} className="card p-4">
                <div className="flex justify-between mb-2">
                  <div className="text-sm font-medium">Жалоба #{c.id}</div>
                  <div className="text-xs text-gray-400">{new Date(c.created_at).toLocaleDateString('ru-RU')}</div>
                </div>
                <div className="text-sm text-gray-600 mb-3">Причина: <strong>{c.reason}</strong></div>
                <div className="flex gap-2">
                  <button onClick={() => resolveComplaint(c.id, 'dismiss')} className="btn-secondary text-sm py-1 px-3">Отклонить</button>
                  <button onClick={() => resolveComplaint(c.id, 'warn')} className="btn text-sm py-1 px-3 bg-yellow-100 text-yellow-700 hover:bg-yellow-200">Предупредить</button>
                  <button onClick={() => resolveComplaint(c.id, 'block')} className="btn-danger text-sm py-1 px-3">Заблокировать</button>
                </div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  )
}
