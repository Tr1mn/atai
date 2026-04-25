import { Link } from 'react-router-dom'

const assistantUrl = import.meta.env.VITE_AI_ASSISTANT_URL || 'https://think-with-me-bot.lovable.app'

const features = [
  {
    title: 'Подбор маршрута',
    text: 'Поможет выбрать направление под интересы, время и компанию.',
  },
  {
    title: 'Советы по сезону',
    text: 'Подскажет, когда лучше ехать на озера, в горы или культурные места.',
  },
  {
    title: 'Бюджет поездки',
    text: 'Сориентирует по формату отдыха и примерным расходам.',
  },
  {
    title: 'Идеи для отдыха',
    text: 'Предложит спокойные, активные, семейные или фото-маршруты.',
  },
  {
    title: 'Подготовка к походу',
    text: 'Напомнит, что взять с собой и какой уровень сложности выбрать.',
  },
]

export default function AIAssistant() {
  return (
    <div className="bg-gray-50">
      <section className="max-w-6xl mx-auto px-4 py-12 md:py-16">
        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-8 items-start">
          <div>
            <span className="badge-blue mb-4">AI подбор путешествия</span>
            <h1 className="text-3xl md:text-5xl font-bold leading-tight mb-4">
              AI ассистент Atai Travel
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mb-6">
              Поможет подобрать маршрут, выбрать сезон, оценить бюджет и найти подходящий формат путешествия по Кыргызстану.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <a
                href={assistantUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-center text-base px-8 py-3 shadow-sm"
              >
                Открыть AI ассистента
              </a>
              <Link
                to="/travel-request"
                className="btn-secondary text-center text-base px-6 py-3"
              >
                Заполнить анкету
              </Link>
            </div>
          </div>

          <div className="card p-5 md:p-6">
            <h2 className="text-xl font-bold mb-4">Чем поможет ассистент</h2>
            <div className="space-y-3">
              {features.map((feature) => (
                <div key={feature.title} className="rounded-lg border border-gray-100 bg-white p-4">
                  <h3 className="font-semibold mb-1">{feature.title}</h3>
                  <p className="text-sm text-gray-500">{feature.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
