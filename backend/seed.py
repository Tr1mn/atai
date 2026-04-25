"""Run once to populate demo data: python seed.py"""
import json
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import User, Package, PackageDate, Partner, Trip
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# --- Users ---
admin = User(email="admin@atai.kg", password_hash=hash_password("admin123"), full_name="Admin", age=30, city="Bishkek", role="admin", status="verified")
partner_user = User(email="partner@nomad.kg", password_hash=hash_password("partner123"), full_name="Nomad Tours", age=35, city="Bishkek", role="partner", status="verified")
user1 = User(email="aizat@mail.kg", password_hash=hash_password("user123"), full_name="Aizat Mamytova", age=25, city="Bishkek", bio="Люблю горы и приключения", interests="hiking,photography,culture", travel_style="adventure", budget_min=5000, budget_max=50000, languages="ru,ky", status="verified", photo_url="https://i.pravatar.cc/150?img=5")
user2 = User(email="temirlan@mail.kg", password_hash=hash_password("user123"), full_name="Temirlan Sydykov", age=28, city="Ош", bio="Путешественник, люблю знакомиться с новыми людьми", interests="culture,food,history", travel_style="mixed", budget_min=3000, budget_max=30000, languages="ru,ky,en", status="active", photo_url="https://i.pravatar.cc/150?img=12")
user3 = User(email="sarah@gmail.com", password_hash=hash_password("user123"), full_name="Sarah Johnson", age=27, city="London", bio="Solo traveler exploring Central Asia", interests="hiking,culture,photography", travel_style="adventure", budget_min=10000, budget_max=80000, languages="en,ru", status="active", photo_url="https://i.pravatar.cc/150?img=9")

for u in [admin, partner_user, user1, user2, user3]:
    db.add(u)
db.flush()

partner = Partner(user_id=partner_user.id, company_name="Nomad Tours Kyrgyzstan", legal_info="LLC Nomad Tours, reg. 12345", partner_type="agency", status="active", commission_rate=12.0)
db.add(partner)
db.flush()

# --- Packages ---
packages_data = [
    {
        "title": "Иссык-Куль: Жемчужина Кыргызстана",
        "description": "Незабываемый отдых на берегу горного озера Иссык-Куль. Пляж, горные прогулки, юрточный лагерь и местная кухня.",
        "destination": "Иссык-Куль",
        "region": "Иссык-Кульская область",
        "price": 15000,
        "duration_days": 5,
        "min_group_size": 2,
        "max_group_size": 12,
        "inclusions": json.dumps(["Проживание в юрте", "3-разовое питание", "Трансфер из Бишкека", "Гид", "Страховка"]),
        "exclusions": json.dumps(["Авиабилеты", "Личные расходы", "Алкоголь"]),
        "cancellation_policy": "Полный возврат > 14 дней. 50% за 7-14 дней. 0% менее 7 дней.",
        "itinerary": json.dumps([
            {"day": 1, "title": "Прибытие в Чолпон-Ату", "description": "Трансфер, заезд, знакомство с группой, ужин у озера"},
            {"day": 2, "title": "Пляж и Боконбаево", "description": "Утро на пляже, после обеда — деревня Боконбаево, демонстрация охоты с беркутом"},
            {"day": 3, "title": "Горный треккинг", "description": "Поход в Сказку — каньон красных скал, пикник"},
            {"day": 4, "title": "Каракол", "description": "Экскурсия в Каракол: православная церковь, дунганская мечеть, базар"},
            {"day": 5, "title": "Отъезд", "description": "Завтрак, свободное время, трансфер в Бишкек"},
        ]),
        "photo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        "difficulty": "easy",
        "travel_style": "mixed",
        "family_friendly": True,
        "family_rates_enabled": True,
        "featured": True,
    },
    {
        "title": "Ала-Арча: Горный треккинг",
        "description": "Классический треккинг по национальному парку Ала-Арча. Альпийские луга, ледники и панорамные виды на горный хребет Тянь-Шань.",
        "destination": "Ала-Арча",
        "region": "Чуйская область",
        "price": 8000,
        "duration_days": 2,
        "min_group_size": 2,
        "max_group_size": 8,
        "inclusions": json.dumps(["Вход в нацпарк", "Гид-проводник", "Снаряжение (базовый комплект)", "Питание на маршруте"]),
        "exclusions": json.dumps(["Трансфер в/из Бишкека", "Личное снаряжение", "Страховка"]),
        "cancellation_policy": "Полный возврат > 14 дней. 50% за 7-14 дней. 0% менее 7 дней.",
        "itinerary": json.dumps([
            {"day": 1, "title": "Треккинг к водопаду Ак-Сай", "description": "Старт у ворот парка, подъем к водопаду (6 км), ночевка в горном лагере"},
            {"day": 2, "title": "Панорама и спуск", "description": "Утренний подъем на смотровую точку 3200м, фото-сессия, спуск"},
        ]),
        "photo_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800",
        "difficulty": "moderate",
        "travel_style": "adventure",
        "family_friendly": False,
        "family_rates_enabled": False,
        "featured": True,
    },
    {
        "title": "Каракол: Культура и природа",
        "description": "Погружение в историю и природу Каракола — самого аутентичного города Кыргызстана. Горячие источники, Джеты-Огуз и ущелье Алтын-Арашан.",
        "destination": "Каракол",
        "region": "Иссык-Кульская область",
        "price": 22000,
        "duration_days": 4,
        "min_group_size": 2,
        "max_group_size": 10,
        "inclusions": json.dumps(["Проживание в гестхаусе", "Завтрак и ужин", "Трансфер Бишкек-Каракол", "Местный гид"]),
        "exclusions": json.dumps(["Обед", "Входные билеты в музеи", "Личные расходы"]),
        "cancellation_policy": "Полный возврат > 14 дней. 50% за 7-14 дней. 0% менее 7 дней.",
        "itinerary": json.dumps([
            {"day": 1, "title": "Прибытие, обзорная экскурсия", "description": "Дунганская мечеть, православная церковь, базар"},
            {"day": 2, "title": "Джеты-Огуз", "description": "Скалы 'Разбитое сердце', ущелье, горячие источники"},
            {"day": 3, "title": "Алтын-Арашан", "description": "Треккинг к термальным источникам (12 км), купание"},
            {"day": 4, "title": "Отъезд", "description": "Свободное утро, трансфер в Бишкек"},
        ]),
        "photo_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800",
        "difficulty": "moderate",
        "travel_style": "mixed",
        "family_friendly": True,
        "family_rates_enabled": True,
        "featured": False,
    },
    {
        "title": "Нарын и Ташрабат: Шёлковый путь",
        "description": "Путешествие по Великому шёлковому пути через Нарын к средневековому каравансараю Ташрабат. Кочевая культура, орлы, горная степь.",
        "destination": "Нарын",
        "region": "Нарынская область",
        "price": 35000,
        "duration_days": 6,
        "min_group_size": 3,
        "max_group_size": 8,
        "inclusions": json.dumps(["Юрта 3 ночи + гестхаус 2 ночи", "Полный пансион", "4x4 трансфер", "Гид", "Охота с беркутом"]),
        "exclusions": json.dumps(["Международный перелет", "Виза", "Страховка"]),
        "cancellation_policy": "Полный возврат > 14 дней. 50% за 7-14 дней. 0% менее 7 дней.",
        "itinerary": json.dumps([
            {"day": 1, "title": "Бишкек → Нарын", "description": "Переезд (350км), ужин, ночевка"},
            {"day": 2, "title": "Нарын: город и крепость", "description": "Осмотр города, нарынская крепость, местный рынок"},
            {"day": 3, "title": "Ташрабат", "description": "Каравансарай XI века, кочевое ранчо, охота с беркутом"},
            {"day": 4, "title": "Перевал Тоо-Ашуу", "description": "Перевал 3400м, высокогорное озеро, юрточный лагерь"},
            {"day": 5, "title": "Кочевая жизнь", "description": "Верховая езда, изготовление кумыса, войлочная мастерская"},
            {"day": 6, "title": "Возвращение в Бишкек", "description": "Трансфер, прощальный обед"},
        ]),
        "photo_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800",
        "difficulty": "moderate",
        "travel_style": "culture",
        "family_friendly": False,
        "family_rates_enabled": False,
        "featured": False,
    },
]

now = datetime.utcnow()
for pdata in packages_data:
    pkg = Package(partner_id=partner.id, status="published", **{k: v for k, v in pdata.items() if k != "featured"}, featured=pdata.get("featured", False))
    db.add(pkg)
    db.flush()
    for i in range(3):
        start = now + timedelta(days=7 + i * 14)
        pd = PackageDate(package_id=pkg.id, start_date=start, total_slots=pkg.max_group_size, available_slots=pkg.max_group_size - (i * 2))
        db.add(pd)

# --- Trips ---
trip1 = Trip(
    organizer_id=user1.id,
    title="Ала-Тоо: ищу попутчиков на выходные!",
    destination="Ала-Арча",
    description="Планирую треккинг в Ала-Арча на выходные. Ищу 2-3 человек со средним уровнем подготовки.",
    start_date=now + timedelta(days=10),
    end_date=now + timedelta(days=12),
    min_size=2, max_size=5,
    budget_min=3000, budget_max=8000,
    travel_style="adventure",
    current_size=1, status="open",
    photo_url="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400",
)
trip2 = Trip(
    organizer_id=user2.id,
    title="Иссык-Куль июль — семейный формат",
    destination="Иссык-Куль",
    description="Едем на Иссык-Куль большой компанией, места ещё есть. Дети welcome.",
    start_date=now + timedelta(days=25),
    end_date=now + timedelta(days=30),
    min_size=4, max_size=12,
    budget_min=10000, budget_max=20000,
    travel_style="relax",
    current_size=3, status="open",
    photo_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
)
db.add(trip1)
db.add(trip2)

db.commit()
print("✅ Seed data created successfully!")
print(f"Admin:   admin@atai.kg / admin123")
print(f"Partner: partner@nomad.kg / partner123")
print(f"User:    aizat@mail.kg / user123")
db.close()
