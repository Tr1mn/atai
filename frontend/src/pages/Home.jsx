import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import PackageCard from '../components/PackageCard'

export default function Home() {
  const [featured, setFeatured] = useState([])

  useEffect(() => {
    api.get('/api/packages/?featured_only=true').then(r => setFeatured(r.data.slice(0, 3))).catch(() => {})
  }, [])

  return (
    <div>
      {/* Hero */}
      <div className="relative h-[520px] flex items-center justify-center text-center overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600"
          alt="Кыргызстан"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60" />
        <div className="relative z-10 text-white px-4">
          <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow">
            Открой Кыргызстан<br />с <span className="text-blue-300">попутчиками</span>
          </h1>
          <p className="text-lg md:text-xl mb-8 text-gray-200 max-w-xl mx-auto">
            Находи единомышленников, бронируй готовые туры и путешествуй безопасно
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/packages" className="btn-primary text-base px-6 py-3">Смотреть туры</Link>
            <Link to="/ai-assistant" className="btn bg-white text-blue-700 text-base px-6 py-3 hover:bg-blue-50">Спросить AI</Link>
            <Link to="/travel-request" className="btn bg-white text-blue-700 text-base px-6 py-3 hover:bg-blue-50">Подобрать маршрут</Link>
            <Link to="/matching" className="btn bg-white/20 backdrop-blur border border-white/40 text-white text-base px-6 py-3 hover:bg-white/30">Найти попутчика</Link>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-blue-700 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-3 gap-4 text-center">
          {[['200+', 'Маршрутов'], ['1,500+', 'Путешественников'], ['50+', 'Партнеров']].map(([val, label]) => (
            <div key={label}><div className="text-3xl font-bold">{val}</div><div className="text-blue-200 text-sm">{label}</div></div>
          ))}
        </div>
      </div>

      {/* AI Assistant */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="card p-6 md:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-5">
          <div>
            <span className="badge-blue mb-3">AI ассистент</span>
            <h2 className="text-2xl font-bold mb-2">Не знаете, куда поехать?</h2>
            <p className="text-gray-500 max-w-2xl">
              AI ассистент поможет подобрать маршрут по интересам, сезону и бюджету.
            </p>
          </div>
          <Link to="/ai-assistant" className="btn-primary text-center whitespace-nowrap px-6 py-3">
            Спросить AI
          </Link>
        </div>
      </div>

      {/* Featured packages */}
      <div className="max-w-7xl mx-auto px-4 py-14">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold">Популярные туры</h2>
          <Link to="/packages" className="text-blue-700 text-sm font-medium hover:underline">Все туры →</Link>
        </div>
        {featured.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {featured.map(pkg => <PackageCard key={pkg.id} pkg={pkg} />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { title: 'Иссык-Куль', desc: 'Горное озеро', img: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400' },
              { title: 'Ала-Арча', desc: 'Треккинг', img: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400' },
              { title: 'Нарын', desc: 'Шёлковый путь', img: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400' },
            ].map(d => (
              <div key={d.title} className="card overflow-hidden">
                <img src={d.img} alt={d.title} className="h-48 w-full object-cover" />
                <div className="p-4"><h3 className="font-semibold">{d.title}</h3><p className="text-sm text-gray-500">{d.desc}</p></div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* How it works */}
      <div className="bg-gray-100 py-14">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-10">Как это работает</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              ['🔍', 'Выбери тур', 'Просматривай каталог туров по Кыргызстану'],
              ['📝', 'Заполни анкету', 'Партнеры предложат маршрут и выгодную цену'],
              ['📋', 'Забронируй', 'Безопасное бронирование с подтверждением'],
              ['🏔️', 'Путешествуй', 'Наслаждайся поездкой с поддержкой 24/7'],
            ].map(([icon, title, desc]) => (
              <div key={title} className="bg-white p-6 rounded-xl shadow-sm">
                <div className="text-4xl mb-3">{icon}</div>
                <h3 className="font-semibold mb-1">{title}</h3>
                <p className="text-sm text-gray-500">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-4xl mx-auto px-4 py-14 text-center">
        <h2 className="text-3xl font-bold mb-4">Готов к приключению?</h2>
        <p className="text-gray-500 mb-6">Заполни анкету, и турагентства предложат маршрут под твой бюджет и интересы</p>
        <Link to="/travel-request" className="btn-primary text-base px-8 py-3">Подобрать тур</Link>
      </div>
    </div>
  )
}
