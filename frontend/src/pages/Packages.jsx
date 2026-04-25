import { useEffect, useState } from 'react'
import api from '../api/client'
import PackageCard from '../components/PackageCard'

export default function Packages() {
  const [packages, setPackages] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ travel_style: '', difficulty: '', family_friendly: '', max_price: '' })

  const load = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (filters.travel_style) params.append('travel_style', filters.travel_style)
    if (filters.difficulty) params.append('difficulty', filters.difficulty)
    if (filters.family_friendly) params.append('family_friendly', filters.family_friendly)
    if (filters.max_price) params.append('max_price', filters.max_price)
    api.get(`/api/packages/?${params}`).then(r => setPackages(r.data)).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const set = (k) => (e) => setFilters(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-2">Туры по Кыргызстану</h1>
      <p className="text-gray-500 mb-8">Готовые пакеты от проверенных партнеров</p>

      {/* Filters */}
      <div className="card p-4 mb-8 flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Стиль</label>
          <select className="input py-1.5 text-sm" value={filters.travel_style} onChange={set('travel_style')}>
            <option value="">Все</option>
            <option value="adventure">Приключения</option>
            <option value="relax">Отдых</option>
            <option value="culture">Культура</option>
            <option value="mixed">Смешанный</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Сложность</label>
          <select className="input py-1.5 text-sm" value={filters.difficulty} onChange={set('difficulty')}>
            <option value="">Все</option>
            <option value="easy">Лёгкий</option>
            <option value="moderate">Средний</option>
            <option value="hard">Сложный</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Семейный</label>
          <select className="input py-1.5 text-sm" value={filters.family_friendly} onChange={set('family_friendly')}>
            <option value="">Любой</option>
            <option value="true">Да</option>
            <option value="false">Нет</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Макс. цена ($)</label>
          <input className="input py-1.5 text-sm w-32" type="number" placeholder="50000" value={filters.max_price} onChange={set('max_price')} />
        </div>
        <button onClick={load} className="btn-primary py-1.5 text-sm">Применить</button>
        <button onClick={() => { setFilters({ travel_style: '', difficulty: '', family_friendly: '', max_price: '' }); setTimeout(load, 0) }} className="btn-secondary py-1.5 text-sm">Сбросить</button>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-400">Загружаем туры...</div>
      ) : packages.length === 0 ? (
        <div className="text-center py-20 text-gray-400">Туры не найдены. Попробуйте изменить фильтры.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {packages.map(pkg => <PackageCard key={pkg.id} pkg={pkg} />)}
        </div>
      )}
    </div>
  )
}
