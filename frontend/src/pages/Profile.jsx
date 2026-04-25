import { useEffect, useState } from 'react'
import api from '../api/client'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get('/api/users/me').then(r => { setProfile(r.data); setForm(r.data) }).finally(() => setLoading(false))
  }, [])

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const { data } = await api.put('/api/users/me', {
        full_name: form.full_name, age: form.age, city: form.city, bio: form.bio,
        photo_url: form.photo_url, interests: form.interests, travel_style: form.travel_style,
        budget_min: form.budget_min, budget_max: form.budget_max, languages: form.languages,
        phone: form.phone || null, telegram: form.telegram || null,
        whatsapp: form.whatsapp || null, instagram: form.instagram || null,
      })
      setProfile(data)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="text-center py-20 text-gray-400">Загружаем...</div>

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Мой профиль</h1>
      <div className="card p-6">
        <div className="flex items-center gap-4 mb-8">
          <img src={form.photo_url || `https://i.pravatar.cc/80?u=${profile.id}`} alt={profile.full_name} className="w-20 h-20 rounded-full object-cover border-4 border-blue-100" />
          <div>
            <div className="font-bold text-xl">{profile.full_name}</div>
            <div className="text-sm text-gray-500">{profile.email}</div>
            <span className={`badge mt-1 ${profile.status === 'verified' ? 'badge-green' : 'badge-blue'}`}>{profile.status === 'verified' ? '✓ Верифицирован' : profile.role}</span>
          </div>
        </div>

        <form onSubmit={save} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Полное имя</label>
              <input className="input" value={form.full_name || ''} onChange={set('full_name')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Возраст</label>
              <input className="input" type="number" value={form.age || ''} onChange={set('age')} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Город</label>
            <input className="input" value={form.city || ''} onChange={set('city')} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">О себе</label>
            <textarea className="input h-24 resize-none" value={form.bio || ''} onChange={set('bio')} placeholder="Расскажи о себе, увлечениях, опыте путешествий..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">URL фото</label>
            <input className="input" value={form.photo_url || ''} onChange={set('photo_url')} placeholder="https://..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Интересы (через запятую)</label>
            <input className="input" value={form.interests || ''} onChange={set('interests')} placeholder="hiking, photography, culture" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Стиль путешествий</label>
            <select className="input" value={form.travel_style || ''} onChange={set('travel_style')}>
              <option value="">Не выбран</option>
              <option value="adventure">Приключения</option>
              <option value="relax">Отдых</option>
              <option value="culture">Культура</option>
              <option value="mixed">Смешанный</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Бюджет от ($)</label>
              <input className="input" type="number" value={form.budget_min || ''} onChange={set('budget_min')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Бюджет до ($)</label>
              <input className="input" type="number" value={form.budget_max || ''} onChange={set('budget_max')} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Языки (через запятую)</label>
            <input className="input" value={form.languages || ''} onChange={set('languages')} placeholder="ru, en, ky" />
          </div>

          <div className="border-t pt-4">
            <p className="text-sm font-semibold text-gray-700 mb-1">Контакты для подбора попутчика</p>
            <p className="text-xs text-gray-400 mb-3">Видны только при взаимной симпатии в разделе «Индивидуальный»</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
                <input className="input" value={form.phone || ''} onChange={set('phone')} placeholder="+996 700 000000" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telegram</label>
                <input className="input" value={form.telegram || ''} onChange={set('telegram')} placeholder="@username" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
                <input className="input" value={form.whatsapp || ''} onChange={set('whatsapp')} placeholder="+996 700 000000" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Instagram</label>
                <input className="input" value={form.instagram || ''} onChange={set('instagram')} placeholder="@username" />
              </div>
            </div>
          </div>

          <button type="submit" disabled={saving} className="btn-primary w-full py-2.5">
            {saving ? 'Сохраняем...' : saved ? '✓ Сохранено!' : 'Сохранить профиль'}
          </button>
        </form>
      </div>
    </div>
  )
}
