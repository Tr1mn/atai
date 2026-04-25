export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between gap-6">
        <div>
          <div className="text-white font-bold text-lg mb-2">🏔️ Atai Travel</div>
          <p className="text-sm">Путешествия по Кыргызстану — находите попутчиков,<br />бронируйте туры, открывайте страну.</p>
        </div>
        <div className="flex gap-12 text-sm">
          <div>
            <div className="text-white font-medium mb-2">Туры</div>
            <ul className="space-y-1"><li>Иссык-Куль</li><li>Каракол</li><li>Нарын</li><li>Ала-Арча</li></ul>
          </div>
          <div>
            <div className="text-white font-medium mb-2">Компания</div>
            <ul className="space-y-1"><li>О нас</li><li>Партнерам</li><li>Контакты</li></ul>
          </div>
        </div>
      </div>
      <div className="text-center text-xs mt-8 text-gray-600">© 2026 Atai Travel. Кыргызстан.</div>
    </footer>
  )
}
