"""Seed database with initial data: categories, services, prices, posts, FAQ, promotions."""
import asyncio
from decimal import Decimal
from datetime import date

from sqlalchemy import select
from app.database import engine, async_session, Base
from app.models import *


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as s:
        # Check if already seeded
        result = await s.execute(select(ServiceCategory))
        if result.scalars().first():
            print("Database already seeded, skipping.")
            return

        print("Seeding database...")

        # ===== CATEGORIES =====
        categories = [
            ServiceCategory(id=1, name="Деликатная мойка", icon="🧽", sort_order=1),
            ServiceCategory(id=2, name="Антигравийная оклейка кузова", icon="🛡️", sort_order=2),
            ServiceCategory(id=3, name="Оклейка виниловой плёнкой", icon="🎨", sort_order=3),
            ServiceCategory(id=4, name="Тонировка стёкол", icon="🕶️", sort_order=4),
            ServiceCategory(id=5, name="Полировка", icon="✨", sort_order=5),
            ServiceCategory(id=6, name="Защитные покрытия", icon="🔰", sort_order=6),
            ServiceCategory(id=7, name="Химчистка салона", icon="🧹", sort_order=7),
            ServiceCategory(id=8, name="Перетяжка и восстановление салона", icon="🪡", sort_order=8),
            ServiceCategory(id=9, name="Шумоизоляция", icon="🔇", sort_order=9),
            ServiceCategory(id=10, name="Антикоррозийная обработка", icon="🛡️", sort_order=10),
            ServiceCategory(id=11, name="Аквапринт", icon="💧", sort_order=11),
            ServiceCategory(id=12, name="Покраска в жидкую резину", icon="🎨", sort_order=12),
        ]
        s.add_all(categories)
        await s.flush()

        # ===== SERVICES & PRICES =====

        # Cat 1: Мойка
        wash_services = [
            ("Эконом: 1-фазная мойка", "Бесконтактная мойка + воск", 0.5, 1.0, True, False,
             [("I", 20), ("II", 25), ("III", 30)]),
            ("Стандарт: 2-фазная мойка", "Бесконтактная мойка + воск (2 фазы)", 0.5, 1.0, True, False,
             [("I", 30), ("II", 35), ("III", 40)]),
            ("Премиум: 3-фазная мойка", "Стандарт + полимерное покрытие", 1.0, 1.5, True, False,
             [("I", 40), ("II", 45), ("III", 50)]),
            ("Комплекс Клин", "Стандарт + уборка салона", 1.5, 2.5, True, False,
             [("I", 50), ("II", 70), ("III", 100)]),
            ("Комплекс Люкс", "Стандарт + полная уборка + чернение шин", 2.0, 3.0, True, False,
             [("I", 65), ("II", 85), ("III", 115)]),
            ("Уборка салона", "Полная уборка салона", 1.0, 2.0, True, False,
             [("I", 30), ("II", 35), ("III", 40)]),
            ("Мойка стёкол и зеркал салона", None, 0.5, 1.0, True, False,
             [("I", 20), ("II", 25), ("III", 35)]),
            ("Обработка кожаных сидений", None, 1.0, 1.5, True, False,
             [("I", 30), ("II", 35), ("III", 40)]),
            ("Обработка пластиковых панелей", "Антистатик", 0.5, 1.0, True, False,
             [("I", 15), ("II", 16), ("III", 18)]),
            ("Мойка двигателя", "Мойка двигателя и подкапотного пространства", 1.0, 2.0, True, False,
             [("I", 120), ("II", 130), ("III", 140)]),
            ("Мойка ковриков", None, 0.5, 0.5, False, False, [(None, 5)]),
            ("Экспресс-химчистка ковриков", "За штуку", 0.5, 1.0, False, False, [(None, 10)]),
            ("Чистка дисков", "За штуку", 0.5, 1.0, False, False, [(None, 20)]),
            ("Удаление битумных загрязнений", None, 1.0, 3.0, False, False, [(None, 100)]),
            ("Обработка резинок от примерзания", None, 0.5, 0.5, False, False, [(None, 10)]),
            ("Чернение шин", None, 0.5, 0.5, False, False, [(None, 10)]),
        ]

        for i, (name, desc, d_min, d_max, has_cc, is_pkg, prices) in enumerate(wash_services):
            svc = Service(category_id=1, name=name, description=desc, duration_min_hours=d_min,
                          duration_max_hours=d_max, has_car_classes=has_cc, is_package=is_pkg, sort_order=i)
            s.add(svc)
            await s.flush()
            for cc, price in prices:
                s.add(ServicePrice(service_id=svc.id, car_class=cc, price_from=Decimal(str(price))))

        # Cat 2: Антигравийная оклейка
        ppf = Service(category_id=2, name="Антигравийная оклейка", is_package=True,
                      description="Защита кузова антигравийной плёнкой. Бренды: GSUIT, Suntek, Hexis, Llumar, UnionDelta. Гарантия 12 мес на работу, до 7 лет на плёнку. Рассрочка 3 и 6 месяцев.",
                      duration_min_hours=8, duration_max_hours=48, sort_order=0)
        s.add(ppf)
        await s.flush()
        ppf_packages = [
            ("MINI", 550, "Полоса над лобовым, оптика, часть капота + подарки: антиманикюр, торцы дверей, антидождь"),
            ("STANDART", 900, "Стойки лобового, часть капота, над лобовым, пороги 4шт, часть крыльев, фары+ПТФ + подарки: антиманикюр, торцы дверей, Krytex Mega Quick, антидождь"),
            ("PREMIUM", 1500, "Полоса задний бампер, пороги, стойки, 2 крыла, под ручками, зеркала, над лобовым, оптика, передний бампер, капот + подарки: жидкое стекло, торцы, антидождь в круг"),
            ("INDIVIDUAL", 2500, "Любые элементы, вплоть до полной оклейки + 6 месяцев обслуживания"),
        ]
        for pkg_name, price, desc in ppf_packages:
            s.add(ServicePrice(service_id=ppf.id, package_name=pkg_name, price_from=Decimal(str(price)), description=desc))

        # Cat 3: Виниловая оклейка
        vinyl = Service(category_id=3, name="Оклейка виниловой плёнкой",
                        description="Изменение цвета/стиля авто", duration_min_hours=8, duration_max_hours=72, sort_order=0)
        s.add(vinyl)
        await s.flush()
        s.add(ServicePrice(service_id=vinyl.id, price_from=Decimal("300"), description="От 300 BYN за элемент"))

        # Cat 4: Тонировка
        tint_services = [
            ("Классическая клеевая тонировка", 50),
            ("Атермальная тонировка", 70),
            ("Съёмная тонировка", 60),
            ("Жёсткая съёмная тонировка", 80),
            ("Растонировка стёкол", 50),
        ]
        for i, (name, price) in enumerate(tint_services):
            svc = Service(category_id=4, name=name, duration_min_hours=1, duration_max_hours=4, sort_order=i)
            s.add(svc)
            await s.flush()
            s.add(ServicePrice(service_id=svc.id, price_from=Decimal(str(price)), description="Цена за стекло"))

        # Cat 5: Полировка
        polish_services = [
            ("Полировка кузова", 50, 3, 8),
            ("Полировка фар", 50, 1, 2),
        ]
        for i, (name, price, d_min, d_max) in enumerate(polish_services):
            svc = Service(category_id=5, name=name, duration_min_hours=d_min, duration_max_hours=d_max, sort_order=i)
            s.add(svc)
            await s.flush()
            s.add(ServicePrice(service_id=svc.id, price_from=Decimal(str(price))))

        # Cat 6: Защитные покрытия
        coating_services = [
            ("Керамика 9H+ (Krytex)", 200, 4, 8),
            ("Жидкое стекло 7H+", 150, 3, 6),
            ("Защитные полироли", 70, 2, 4),
            ("Антидождь (нанопокрытие на стёкла)", 70, 1, 2),
        ]
        for i, (name, price, d_min, d_max) in enumerate(coating_services):
            svc = Service(category_id=6, name=name, duration_min_hours=d_min, duration_max_hours=d_max, sort_order=i)
            s.add(svc)
            await s.flush()
            s.add(ServicePrice(service_id=svc.id, price_from=Decimal(str(price))))

        # Cat 7: Химчистка салона
        chem_services = [
            ("Химчистка Ecoclean", True, 10, 14,
             [("I", 250), ("II", 300), ("III", 350)]),
            ("Защита кожи Krytex MEGA Leather", True, 4, 6,
             [("I", 300), ("II", 330), ("III", 370)]),
            ("Защита ткани Krytex MEGA Tex", True, 14, 18,
             [("I", 250), ("II", 280), ("III", 310)]),
        ]
        for i, (name, has_cc, d_min, d_max, prices) in enumerate(chem_services):
            svc = Service(category_id=7, name=name, has_car_classes=has_cc,
                          duration_min_hours=d_min, duration_max_hours=d_max, sort_order=i)
            s.add(svc)
            await s.flush()
            for cc, price in prices:
                s.add(ServicePrice(service_id=svc.id, car_class=cc, price_from=Decimal(str(price))))

        # Cat 8: Перетяжка
        upholstery = [
            ("Перетяжка салона", 50, 8, 48),
            ("Перетяжка руля", 50, 2, 4),
            ("Перетяжка потолка", 50, 4, 8),
            ("Восстановление и ремонт кожи", 50, 2, 8),
        ]
        for i, (name, price, d_min, d_max) in enumerate(upholstery):
            svc = Service(category_id=8, name=name, duration_min_hours=d_min, duration_max_hours=d_max, sort_order=i,
                          description="Цена за элемент")
            s.add(svc)
            await s.flush()
            s.add(ServicePrice(service_id=svc.id, price_from=Decimal(str(price))))

        # Cat 9: Шумоизоляция
        svc = Service(category_id=9, name="Шумоизоляция", description="Полная и частичная",
                      duration_min_hours=4, duration_max_hours=24, sort_order=0)
        s.add(svc)
        await s.flush()
        s.add(ServicePrice(service_id=svc.id, price_from=Decimal("100")))

        # Cat 10: Антикор
        svc = Service(category_id=10, name="Антикоррозийная обработка",
                      description="Комплексная обработка днища и арок",
                      duration_min_hours=4, duration_max_hours=8, sort_order=0)
        s.add(svc)
        await s.flush()
        s.add(ServicePrice(service_id=svc.id, price_from=Decimal("100")))

        # Cat 11: Аквапринт
        svc = Service(category_id=11, name="Аквапринт",
                      description="Декорирование под дерево, карбон, алюминий, титан. Цена за элемент.",
                      duration_min_hours=4, duration_max_hours=24, sort_order=0)
        s.add(svc)
        await s.flush()
        s.add(ServicePrice(service_id=svc.id, price_from=Decimal("50")))

        # Cat 12: Жидкая резина
        svc = Service(category_id=12, name="Покраска в жидкую резину",
                      description="Полная и частичная покраска. Цена за элемент.",
                      duration_min_hours=4, duration_max_hours=48, sort_order=0)
        s.add(svc)
        await s.flush()
        s.add(ServicePrice(service_id=svc.id, price_from=Decimal("50")))

        # ===== WORK POSTS =====
        posts = [
            WorkPost(name="Пост 1 (Мойка)", specialization="Мойка, химчистка"),
            WorkPost(name="Пост 2 (Оклейка)", specialization="Антигравийная оклейка, винил"),
            WorkPost(name="Пост 3 (Полировка/Защита)", specialization="Полировка, керамика, покрытия"),
            WorkPost(name="Пост 4 (Универсальный)", specialization="Перетяжка, шумоизоляция, аквапринт"),
        ]
        s.add_all(posts)

        # ===== FAQ =====
        faqs = [
            # Антигравийная плёнка
            FAQ(category="Антигравийная плёнка", question="Что такое антигравийная плёнка (PPF)?",
                answer="Антигравийная плёнка (Paint Protection Film) — это прозрачная полиуретановая плёнка, которая наклеивается на кузов автомобиля для защиты от сколов, царапин, песка и реагентов. Плёнка самовосстанавливающаяся — мелкие царапины затягиваются при нагреве.", sort_order=1),
            FAQ(category="Антигравийная плёнка", question="Сколько держится антигравийная плёнка?",
                answer="Срок службы зависит от качества плёнки и условий эксплуатации. Премиальные плёнки (Suntek, Llumar, Hexis) служат 5-7 лет. Мы даём гарантию 12 месяцев на работу.", sort_order=2),
            FAQ(category="Антигравийная плёнка", question="Можно ли мыть машину после оклейки?",
                answer="Да, но рекомендуем подождать 3-5 дней после оклейки. После этого можно мыть как обычно. Избегайте агрессивных щёток на автоматических мойках.", sort_order=3),
            FAQ(category="Антигравийная плёнка", question="Видна ли плёнка на кузове?",
                answer="Качественная плёнка практически невидима. После профессиональной установки заметить её можно только при близком осмотре краёв. Глянцевая плёнка не меняет внешний вид автомобиля.", sort_order=4),
            FAQ(category="Антигравийная плёнка", question="Какие бренды плёнок вы используете?",
                answer="Мы работаем с лучшими мировыми брендами: GSUIT, Suntek, Hexis, Llumar, UnionDelta. Каждый бренд имеет свои преимущества — поможем подобрать оптимальный вариант.", sort_order=5),
            FAQ(category="Антигравийная плёнка", question="Есть ли рассрочка на оклейку?",
                answer="Да! Мы предлагаем рассрочку на 3 и 6 месяцев без первоначального платежа. Подробности уточняйте у менеджера.", sort_order=6),
            FAQ(category="Антигравийная плёнка", question="Сколько времени занимает оклейка?",
                answer="Зависит от объёма работ. Частичная оклейка (пакет MINI) — 1 день. Полная оклейка кузова — 3-5 дней. Точные сроки обсуждаем при записи.", sort_order=7),
            FAQ(category="Антигравийная плёнка", question="Что входит в подарки к пакетам?",
                answer="MINI: антиманикюр, торцы дверей, антидождь. STANDART: антиманикюр, торцы, Krytex Mega Quick, антидождь. PREMIUM: жидкое стекло, торцы, антидождь в круг. INDIVIDUAL: 6 мес обслуживания.", sort_order=8),

            # Химчистка
            FAQ(category="Химчистка", question="Сколько длится химчистка салона?",
                answer="Комплексная химчистка составами Ecoclean занимает от 10 часов. С защитой ткани/кожи — от 14 часов. Рекомендуем оставить автомобиль на целый день.", sort_order=1),
            FAQ(category="Химчистка", question="Какие классы авто вы выделяете?",
                answer="I класс — седаны до бизнес-класса (Golf, Focus, Solaris). II класс — бизнес-седаны и компактные кроссоверы (RAV4, Tiguan, Mazda 6). III класс — большие седаны и полноразмерные кроссоверы (BMW 7, X-Trail, Audi Q5).", sort_order=2),

            # Мойка
            FAQ(category="Мойка", question="Чем отличаются фазы мойки?",
                answer="1-фазная (Эконом) — бесконтактная мойка + воск. 2-фазная (Стандарт) — двухэтапная бесконтактная мойка + воск. 3-фазная (Премиум) — стандарт + нанесение полимерного покрытия для дополнительной защиты.", sort_order=1),
            FAQ(category="Мойка", question="Что входит в Комплекс Люкс?",
                answer="Стандартная 2-фазная мойка + полная уборка салона (пылесос, протирка панелей, стёкол) + чернение шин. Самый полный вариант ухода за автомобилем.", sort_order=2),

            # Общие
            FAQ(category="Общие вопросы", question="Где вы находитесь?",
                answer="г. Минск, ул. Петруся Бровки 30, К.11. Рядом есть бесплатная парковка.", sort_order=1),
            FAQ(category="Общие вопросы", question="Какой режим работы?",
                answer="ПН-ПТ: 9:00 — 19:00, СБ: 9:00 — 18:00, ВС: выходной.", sort_order=2),
            FAQ(category="Общие вопросы", question="Есть ли парковка?",
                answer="Да, рядом с нашим центром есть бесплатная парковка для клиентов.", sort_order=3),
            FAQ(category="Общие вопросы", question="Предоставляете ли вы рассрочку?",
                answer="Да, рассрочка доступна на услуги оклейки — 3 и 6 месяцев без первоначального платежа.", sort_order=4),
            FAQ(category="Общие вопросы", question="Как работает программа лояльности?",
                answer="Кэшбэк 5% от каждого визита начисляется бонусами. Бонусами можно оплатить до 20% стоимости следующей услуги. За приглашённого друга — 50 BYN бонусов, друг получает 20 BYN.", sort_order=5),
        ]
        s.add_all(faqs)

        # ===== PROMOTIONS =====
        promotions = [
            Promotion(
                title="Сертификат 300 BYN на антикор при оклейке",
                description="При заказе антигравийной оклейки — сертификат на 300 BYN на антикоррозийную обработку в подарок!",
                discount_type=DiscountType.GIFT,
                date_start=date(2025, 1, 1),
                date_end=date(2025, 6, 30),
            ),
            Promotion(
                title="Рассрочка без первоначального платежа",
                description="Оклейка антигравийной плёнкой в рассрочку на 3 или 6 месяцев без первого взноса!",
                discount_type=DiscountType.GIFT,
                date_start=date(2025, 1, 1),
                date_end=date(2025, 12, 31),
            ),
            Promotion(
                title="Бонусы до 30% для постоянных клиентов",
                description="Накапливайте бонусы с каждого визита и экономьте на следующих услугах!",
                discount_type=DiscountType.PERCENT,
                discount_value=Decimal("30"),
                date_start=date(2025, 1, 1),
                date_end=date(2025, 12, 31),
            ),
        ]
        s.add_all(promotions)

        await s.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
