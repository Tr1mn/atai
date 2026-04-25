import { Link } from 'react-router-dom'

const difficultyLabel = { easy: 'Лёгкий', moderate: 'Средний', hard: 'Сложный' }
const styleLabel = { adventure: 'Приключения', relax: 'Отдых', culture: 'Культура', mixed: 'Смешанный' }

export default function PackageCard({ pkg }) {
  return (
    <Link to={`/packages/${pkg.id}`} className="card overflow-hidden hover:shadow-md transition-shadow group block">
      <div className="relative h-48 overflow-hidden">
        <img
          src={pkg.photo_url || 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400'}
          alt={pkg.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {pkg.featured && (
          <span className="absolute top-2 left-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-0.5 rounded-full">⭐ Топ</span>
        )}
        <span className="absolute top-2 right-2 bg-white/90 text-gray-700 text-xs font-medium px-2 py-0.5 rounded-full">
          {pkg.duration_days} дн.
        </span>
      </div>
      <div className="p-4">
        <div className="flex gap-2 mb-2">
          <span className="badge-blue">{difficultyLabel[pkg.difficulty] || pkg.difficulty}</span>
          <span className="badge bg-purple-100 text-purple-800">{styleLabel[pkg.travel_style] || pkg.travel_style}</span>
          {pkg.family_friendly && <span className="badge bg-pink-100 text-pink-800">👨‍👩‍👧 Семейный</span>}
        </div>
        <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">{pkg.title}</h3>
        <p className="text-sm text-gray-500 mb-3 line-clamp-2">{pkg.description}</p>
        <div className="flex items-center justify-between">
          <span className="text-blue-700 font-bold text-lg">{pkg.price.toLocaleString()} $</span>
          <span className="text-xs text-gray-400">📍 {pkg.destination}</span>
        </div>
      </div>
    </Link>
  )
}
