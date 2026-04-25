import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

const interests = [
  ['nature', 'Природа'],
  ['mountains', 'Горы'],
  ['lakes', 'Озёра'],
  ['culture', 'Культура и история'],
  ['active', 'Активный отдых'],
  ['relax', 'Спокойный отдых'],
  ['photo', 'Фото и контент'],
  ['food', 'Гастрономия'],
  ['nomad', 'Кочевая культура'],
]

const activities = [
  ['beach', 'Пляжный отдых'],
  ['walks', 'Лёгкие прогулки'],
  ['trekking', 'Горные походы'],
  ['horse', 'Конные прогулки'],
  ['rafting', 'Рафтинг'],
  ['hot_springs', 'Горячие источники'],
  ['history', 'Исторические места'],
  ['yurt', 'Ночёвка в юрте'],
  ['photo_tour', 'Фототур'],
]

const places = [
  'Иссык-Куль: Чолпон-Ата, Бостери',
  'Южный берег Иссык-Куля',
  'Каракол',
  'Ала-Куль',
  'Алтын-Арашан',
  'Джети-Огуз',
  'Каньон Сказка',
  'Сон-Куль',
  'Ала-Арча',
  'Чон-Кемин',
  'Ош и Сулайман-Тоо',
  'Таш-Рабат',
  'Сары-Челек',
  'Арсланбоб',
  'Кель-Суу',
  'Алайская долина и Пик Ленина',
  'Не знаю, хочу рекомендацию',
]

const initialForm = {
  origin: '',
  days: '',
  companions: '',
  interests: [],
  travel_format: '',
  mood: '',
  difficulty: '',
  budget: '',
  season: '',
  accommodation: '',
  transport: '',
  activities: [],
  preferred_places: [],
  distance: '',
  priority: '',
  notes: '',
}

function ChoiceGroup({ options, value, onChange }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
      {options.map(([key, label]) => (
        <button
          type="button"
          key={key}
          onClick={() => onChange(key)}
          className={`text-left px-3 py-2 rounded-lg border text-sm transition ${
            value === key ? 'border-blue-700 bg-blue-50 text-blue-800' : 'border-gray-200 bg-white hover:border-blue-300'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}

function MultiChoice({ options, values, onToggle }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((item) => {
        const key = Array.isArray(item) ? item[0] : item
        const label = Array.isArray(item) ? item[1] : item
        const active = values.includes(key)
        return (
          <button
            type="button"
            key={key}
            onClick={() => onToggle(key)}
            className={`px-3 py-2 rounded-full border text-sm transition ${
              active ? 'border-blue-700 bg-blue-700 text-white' : 'border-gray-200 bg-white hover:border-blue-300'
            }`}
          >
            {label}
          </button>
        )
      })}
    </div>
  )
}

export default function TravelRequestForm() {
  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))
  const toggle = (key, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: prev[key].includes(value)
        ? prev[key].filter((item) => item !== value)
        : [...prev[key], value],
    }))
  }

  const validate = () => {
    if (!form.origin.trim()) return 'Укажите, откуда вы начинаете путешествие'
    if (!form.days) return 'Выберите количество дней'
    if (!form.companions) return 'Выберите, с кем вы едете'
    if (form.interests.length === 0) return 'Выберите хотя бы один интерес'
    if (!form.travel_format) return 'Выберите формат путешествия'
    if (!form.difficulty) return 'Выберите уровень сложности'
    if (!form.budget) return 'Выберите бюджет'
    if (!form.season) return 'Выберите сезон'
    if (!form.priority) return 'Выберите, что для вас самое важное'
    return ''
  }

  const submit = async (e) => {
    e.preventDefault()
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setError('')
    setSubmitting(true)
    try {
      await api.post('/api/travel-requests/', form)
      navigate('/my-requests')
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось отправить анкету')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="mb-8">
        <p className="text-sm font-semibold text-blue-700 mb-2">Персональный подбор</p>
        <h1 className="text-3xl font-bold mb-3">Анкета для подбора тура по Кыргызстану</h1>
        <p className="text-gray-600 max-w-3xl">
          Ответьте на короткие вопросы, а проверенные турагентства предложат маршрут, пакет и цену под ваш запрос.
        </p>
      </div>

      <form onSubmit={submit} className="space-y-6">
        <section className="card p-5 space-y-5">
          <h2 className="font-semibold text-lg">Базовая информация</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">1. Откуда вы начинаете путешествие?</label>
            <input className="input" value={form.origin} onChange={(e) => set('origin', e.target.value)} placeholder="Например: Бишкек, Ош, Алматы" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">2. Сколько дней хотите путешествовать?</label>
            <ChoiceGroup
              value={form.days}
              onChange={(value) => set('days', value)}
              options={[['1', '1 день'], ['2-3', '2–3 дня'], ['4-6', '4–6 дней'], ['7-10', '7–10 дней'], ['10+', 'Больше 10 дней'], ['unknown', 'Пока не знаю']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">3. С кем вы едете?</label>
            <ChoiceGroup
              value={form.companions}
              onChange={(value) => set('companions', value)}
              options={[['solo', 'Один/одна'], ['couple', 'С парой'], ['friends', 'С друзьями'], ['family', 'С семьёй'], ['kids', 'С детьми'], ['group', 'С группой']]}
            />
          </div>
        </section>

        <section className="card p-5 space-y-5">
          <h2 className="font-semibold text-lg">Интересы и формат</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">4. Что вам интересно? Можно выбрать несколько вариантов.</label>
            <MultiChoice options={interests} values={form.interests} onToggle={(value) => toggle('interests', value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">5. Какой формат путешествия вам ближе?</label>
            <ChoiceGroup
              value={form.travel_format}
              onChange={(value) => set('travel_format', value)}
              options={[['day_trip', 'Однодневная поездка'], ['short_tour', 'Тур на 2–3 дня'], ['week_route', 'Недельный маршрут'], ['trekking', 'Поход/треккинг'], ['comfortable', 'Комфортный тур'], ['budget', 'Бюджетное путешествие']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">6. Какой отдых хочется по настроению?</label>
            <ChoiceGroup
              value={form.mood}
              onChange={(value) => set('mood', value)}
              options={[['calm', 'Спокойный и красивый'], ['active_soft', 'Активный, но без перегруза'], ['adventure', 'Приключенческий'], ['learning', 'Познавательный'], ['romantic', 'Романтичный'], ['family', 'Семейный']]}
            />
          </div>
        </section>

        <section className="card p-5 space-y-5">
          <h2 className="font-semibold text-lg">Бюджет, сезон и комфорт</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">7. Какой уровень сложности вам подходит?</label>
            <ChoiceGroup
              value={form.difficulty}
              onChange={(value) => set('difficulty', value)}
              options={[['easy', 'Лёгкий'], ['moderate', 'Средний'], ['hard', 'Сложный'], ['extreme', 'Экстремальный']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">8. Какой бюджет вам комфортен?</label>
            <ChoiceGroup
              value={form.budget}
              onChange={(value) => set('budget', value)}
              options={[['economy', 'Эконом'], ['middle', 'Средний'], ['comfort', 'Комфорт'], ['premium', 'Премиум']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">9. В какой сезон хотите поехать?</label>
            <ChoiceGroup
              value={form.season}
              onChange={(value) => set('season', value)}
              options={[['spring', 'Весна'], ['summer', 'Лето'], ['autumn', 'Осень'], ['winter', 'Зима'], ['recommend', 'Не знаю, хочу рекомендацию']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">10. Что важнее в проживании?</label>
            <ChoiceGroup
              value={form.accommodation}
              onChange={(value) => set('accommodation', value)}
              options={[['simple', 'Недорого и просто'], ['clean', 'Чисто и удобно'], ['yurt', 'Юрты и местный колорит'], ['hotel', 'Отель или гостевой дом'], ['comfort', 'Максимальный комфорт'], ['any', 'Не важно']]}
            />
          </div>
        </section>

        <section className="card p-5 space-y-5">
          <h2 className="font-semibold text-lg">Маршрут и места</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">11. Какой транспорт вам удобнее?</label>
            <ChoiceGroup
              value={form.transport}
              onChange={(value) => set('transport', value)}
              options={[['car', 'Легковая машина'], ['minivan', 'Минивэн'], ['bus', 'Групповой автобус'], ['walking', 'Пеший маршрут'], ['horse', 'Конная прогулка'], ['any', 'Не важно']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">12. Какие активности вам интересны?</label>
            <MultiChoice options={activities} values={form.activities} onToggle={(value) => toggle('activities', value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">13. Какие места Кыргызстана вам интересны?</label>
            <MultiChoice options={places} values={form.preferred_places} onToggle={(value) => toggle('preferred_places', value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">14. Насколько далеко от города вы готовы ехать?</label>
            <ChoiceGroup
              value={form.distance}
              onChange={(value) => set('distance', value)}
              options={[['1h', 'До 1 часа'], ['2-4h', '2–4 часа'], ['5-8h', '5–8 часов'], ['full_day', 'Можно ехать целый день'], ['remote', 'Готов/готова к удалённым местам']]}
            />
          </div>
        </section>

        <section className="card p-5 space-y-5">
          <h2 className="font-semibold text-lg">Финальный вопрос</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">15. Что для вас самое важное в путешествии?</label>
            <ChoiceGroup
              value={form.priority}
              onChange={(value) => set('priority', value)}
              options={[['beautiful_views', 'Красивые виды'], ['comfort', 'Комфорт'], ['price', 'Цена'], ['safety', 'Безопасность'], ['unique', 'Уникальный опыт'], ['adventure', 'Активность и приключения'], ['culture', 'Культура и традиции'], ['photo', 'Хорошие фото'], ['slow', 'Отдых без спешки']]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Комментарий для турагентств</label>
            <textarea
              className="input h-24 resize-none"
              value={form.notes}
              onChange={(e) => set('notes', e.target.value)}
              placeholder="Например: хотим выгодную цену, без сложных подъёмов, желательно с юртой и горячими источниками"
            />
          </div>
        </section>

        <div className="card p-5 bg-blue-50 border-blue-100">
          <h2 className="font-semibold text-blue-900 mb-2">На основе ответов система сможет предложить подходящие маршруты</h2>
          <p className="text-sm text-blue-800">
            Турагентства увидят ваш запрос и отправят варианты маршрута, цену, длительность и что включено в пакет.
          </p>
        </div>

        {error && <div className="text-sm text-red-700 bg-red-50 border border-red-100 px-4 py-3 rounded-lg">{error}</div>}

        <button type="submit" disabled={submitting} className="btn-primary w-full py-3 text-base">
          {submitting ? 'Отправляем анкету...' : 'Отправить анкету турагентствам'}
        </button>
      </form>
    </div>
  )
}
