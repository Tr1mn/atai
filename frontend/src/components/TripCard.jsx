import { Link } from 'react-router-dom'

const statusLabel = { open: { label: 'Набор открыт', cls: 'badge-green' }, group_formed: { label: 'Группа собрана', cls: 'badge-blue' } }

export default function TripCard({ trip }) {
  const s = statusLabel[trip.status] || { label: trip.status, cls: 'badge-yellow' }
  const start = new Date(trip.start_date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  const end = new Date(trip.end_date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  return (
    <Link to={`/trips/${trip.id}`} className="card overflow-hidden hover:shadow-md transition-shadow block group">
      <div className="h-36 overflow-hidden">
        <img
          src={trip.photo_url || 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400'}
          alt={trip.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className={s.cls}>{s.label}</span>
          <span className="text-xs text-gray-500">{start} — {end}</span>
        </div>
        <h3 className="font-semibold text-gray-900 mb-1">{trip.title}</h3>
        <p className="text-sm text-gray-500 line-clamp-2 mb-2">{trip.description}</p>
        <div className="flex justify-between text-xs text-gray-500">
          <span>📍 {trip.destination}</span>
          <span>👥 {trip.current_size}/{trip.max_size}</span>
        </div>
      </div>
    </Link>
  )
}
