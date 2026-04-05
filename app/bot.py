import asyncio
import re
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from app.core.config import settings
from app.bootstrap import AppContainer
from app.models.user_profile import TimeWindow
from app.services.telegram_service import TelegramFormatter


container = AppContainer()
container.seed_demo_catalog()

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def normalize_day_name(raw_day: str) -> str | None:
    mapping = {
        "monday": "monday", "mon": "monday", "понедельник": "monday", "пн": "monday",
        "tuesday": "tuesday", "tue": "tuesday", "вторник": "tuesday", "вт": "tuesday",
        "wednesday": "wednesday", "wed": "wednesday", "среда": "wednesday", "ср": "wednesday",
        "thursday": "thursday", "thu": "thursday", "четверг": "thursday", "чт": "thursday",
        "friday": "friday", "fri": "friday", "пятница": "friday", "пт": "friday",
        "saturday": "saturday", "sat": "saturday", "суббота": "saturday", "сб": "saturday",
        "sunday": "sunday", "sun": "sunday", "воскресенье": "sunday", "вс": "sunday",
    }
    return mapping.get(raw_day.strip().lower())


def parse_time_windows(raw_text: str) -> list[TimeWindow] | None:
    chunks = [chunk.strip() for chunk in raw_text.split(",") if chunk.strip()]
    result: list[TimeWindow] = []

    for chunk in chunks:
        match = re.fullmatch(r"(\d{2}:\d{2})-(\d{2}:\d{2})", chunk)
        if not match:
            return None

        start, end = match.groups()
        if start >= end:
            return None

        result.append(TimeWindow(start=start, end=end))

    return result


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет. Я Food AI Agent.\n\n"
        "Я умею:\n"
        "• сохранять твои предпочтения\n"
        "• строить план питания на день и неделю\n"
        "• учитывать бюджет\n"
        "• учитывать время доставки\n"
        "• показывать каталог и безопасные блюда\n"
        "• управлять стоп-листом\n\n"
        "Команды:\n"
        "/prefs <текст>\n"
        "/profile\n"
        "/calories <число>\n"
        "/meals <число>\n"
        "/budget <число>\n"
        "/budget clear\n"
        "/plan\n"
        "/week\n"
        "/strict <soft|hard>\n"
        "/schedule\n"
        "/catalog\n"
        "/forbidden\n"
        "/help"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n\n"
        "/prefs <текст> — обновить предпочтения\n"
        "/profile — показать профиль\n"
        "/calories 2200 — задать цель по калориям\n"
        "/meals 3 — задать число приёмов пищи в день\n"
        "/budget 1200 — задать дневной бюджет\n"
        "/budget clear — убрать ограничение бюджета\n"
        "/plan — построить дневной план\n"
        "/week — построить недельный план\n"
        "/strict soft — dislikes только штрафуют\n"
        "/strict hard — dislikes полностью исключаются\n"
        "/schedule — показать текущее расписание\n"
        "/schedule set monday 08:00-09:30,16:00-21:00 — задать окна\n"
        "/schedule clear sunday — очистить окна дня\n"
        "/schedule reset — вернуть дефолтное расписание\n"
        "/catalog — показать весь каталог\n"
        "/catalog safe — показать безопасные блюда под твой профиль\n"
        "/forbidden — показать стоп-лист\n"
        "/forbidden add strawberry — добавить продукт\n"
        "/forbidden remove strawberry — удалить продукт\n"
        "/forbidden clear — очистить стоп-лист\n"
        "/help — показать помощь"
    )


@dp.message(Command("prefs"))
async def cmd_prefs(message: Message):
    user_id = str(message.from_user.id)

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "После /prefs передай текст с предпочтениями.\n\n"
            "Пример:\n"
            "/prefs У меня аллергия на milk, eggs. Не люблю fish и broccoli. Люблю chicken, rice. Мне нужно 2200 ккал. Бюджет 1200 руб."
        )
        return

    user_message = parts[1]

    profile = container.orchestrator.update_preferences(
        user_id=user_id,
        user_message=user_message,
    )
    container.ensure_default_schedule(user_id)

    await message.answer("✅ Предпочтения обновлены.")
    await message.answer(TelegramFormatter.format_profile(profile))
    await message.answer(TelegramFormatter.format_schedule(profile))


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    await message.answer(TelegramFormatter.format_profile(profile))
    await message.answer(TelegramFormatter.format_schedule(profile))
    await message.answer(TelegramFormatter.format_forbidden(profile))


@dp.message(Command("calories"))
async def cmd_calories(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Используй: /calories 2200")
        return

    try:
        calories = int(parts[1].strip())
    except ValueError:
        await message.answer("Некорректное значение. Пример: /calories 2200")
        return

    if calories < 500 or calories > 6000:
        await message.answer("Допустимый диапазон: от 500 до 6000 ккал.")
        return

    updated = container.orchestrator.update_calorie_target(user_id, calories)
    await message.answer(f"✅ Цель по калориям обновлена: {calories}")
    await message.answer(TelegramFormatter.format_profile(updated))


@dp.message(Command("meals"))
async def cmd_meals(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Используй: /meals 3")
        return

    try:
        meal_count = int(parts[1].strip())
    except ValueError:
        await message.answer("Некорректное значение. Пример: /meals 3")
        return

    if meal_count < 1 or meal_count > 6:
        await message.answer("Допустимое число приёмов пищи: от 1 до 6.")
        return

    updated = container.orchestrator.update_daily_meal_count(user_id, meal_count)
    await message.answer(f"✅ Число приёмов пищи обновлено: {meal_count}")
    await message.answer(TelegramFormatter.format_profile(updated))


@dp.message(Command("budget"))
async def cmd_budget(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Используй:\n"
            "/budget 1200\n"
            "/budget clear"
        )
        return

    value = parts[1].strip().lower()

    if value == "clear":
        updated = container.orchestrator.update_budget(user_id, None)
        await message.answer("✅ Ограничение по бюджету убрано.")
        await message.answer(TelegramFormatter.format_profile(updated))
        return

    try:
        budget = float(value.replace(",", "."))
    except ValueError:
        await message.answer("Некорректное значение. Пример: /budget 1200")
        return

    if budget < 100 or budget > 10000:
        await message.answer("Допустимый дневной бюджет: от 100 до 10000.")
        return

    updated = container.orchestrator.update_budget(user_id, budget)
    await message.answer(f"✅ Дневной бюджет обновлён: {budget}")
    await message.answer(TelegramFormatter.format_profile(updated))


@dp.message(Command("strict"))
async def cmd_strict(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:
        current_mode = "жёсткий" if profile.dislike_mode == "hard" else "мягкий"
        await message.answer(
            f"Текущий режим dislikes: {current_mode}\n\n"
            "Используй:\n"
            "/strict soft — dislikes только штрафуют\n"
            "/strict hard — dislikes полностью исключаются"
        )
        return

    mode = parts[1].strip().lower()
    updated_profile = container.orchestrator.update_dislike_mode(user_id, mode)

    if not updated_profile:
        await message.answer("Некорректный режим. Используй /strict soft или /strict hard")
        return

    mode_label = "жёсткий" if mode == "hard" else "мягкий"
    await message.answer(f"✅ Режим dislikes обновлён: {mode_label}")
    await message.answer(TelegramFormatter.format_profile(updated_profile))


@dp.message(Command("schedule"))
async def cmd_schedule(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=3)

    if len(parts) == 1:
        await message.answer(TelegramFormatter.format_schedule(profile))
        return

    action = parts[1].strip().lower()

    if action == "reset":
        updated = container.reset_default_schedule(user_id)
        await message.answer("✅ Дефолтное расписание восстановлено.")
        await message.answer(TelegramFormatter.format_schedule(updated))
        return

    if action == "clear":
        if len(parts) < 3:
            await message.answer("Используй: /schedule clear sunday")
            return

        day_name = normalize_day_name(parts[2])
        if not day_name:
            await message.answer("Не удалось распознать день недели.")
            return

        updated = container.orchestrator.clear_day_schedule(user_id, day_name)
        await message.answer("✅ Окна доставки для выбранного дня очищены.")
        await message.answer(TelegramFormatter.format_schedule(updated))
        return

    if action == "set":
        if len(parts) < 4:
            await message.answer(
                "Используй формат:\n"
                "/schedule set monday 08:00-09:30,16:00-21:00"
            )
            return

        day_name = normalize_day_name(parts[2])
        if not day_name:
            await message.answer("Не удалось распознать день недели.")
            return

        windows = parse_time_windows(parts[3])
        if windows is None:
            await message.answer(
                "Некорректный формат времени.\n"
                "Пример:\n"
                "/schedule set monday 08:00-09:30,16:00-21:00"
            )
            return

        updated = container.orchestrator.set_day_schedule(user_id, day_name, windows)
        await message.answer("✅ Расписание обновлено.")
        await message.answer(TelegramFormatter.format_schedule(updated))
        return

    await message.answer(
        "Неизвестная команда для /schedule.\n\n"
        "Доступно:\n"
        "/schedule\n"
        "/schedule set monday 08:00-09:30,16:00-21:00\n"
        "/schedule clear sunday\n"
        "/schedule reset"
    )


@dp.message(Command("catalog"))
async def cmd_catalog(message: Message):
    user_id = str(message.from_user.id)
    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) == 1:
        meals = container.orchestrator.get_catalog()
        await message.answer(TelegramFormatter.format_catalog(meals, "📚 Полный каталог"))
        return

    subcommand = parts[1].strip().lower()

    if subcommand == "safe":
        profile = container.user_repository.get_user_profile(user_id)
        if not profile:
            await message.answer("Профиль не найден. Сначала используй /prefs")
            return

        meals = container.orchestrator.get_safe_catalog(user_id)
        await message.answer(TelegramFormatter.format_catalog(meals, "✅ Безопасные блюда"))
        return

    await message.answer(
        "Доступно:\n"
        "/catalog — показать весь каталог\n"
        "/catalog safe — показать безопасные блюда под твой профиль"
    )


@dp.message(Command("forbidden"))
async def cmd_forbidden(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=2)

    if len(parts) == 1:
        await message.answer(TelegramFormatter.format_forbidden(profile))
        return

    action = parts[1].strip().lower()

    if action == "clear":
        updated = container.orchestrator.clear_forbidden_products(user_id)
        await message.answer("✅ Стоп-лист очищен.")
        await message.answer(TelegramFormatter.format_forbidden(updated))
        return

    if action in {"add", "remove"}:
        if len(parts) < 3:
            await message.answer(
                "Используй:\n"
                "/forbidden add strawberry\n"
                "/forbidden remove strawberry"
            )
            return

        product = parts[2].strip()

        if action == "add":
            updated = container.orchestrator.add_forbidden_product(user_id, product)
            await message.answer(f"✅ Добавлено в стоп-лист: {product}")
            await message.answer(TelegramFormatter.format_forbidden(updated))
            return

        if action == "remove":
            updated = container.orchestrator.remove_forbidden_product(user_id, product)
            await message.answer(f"✅ Удалено из стоп-листа: {product}")
            await message.answer(TelegramFormatter.format_forbidden(updated))
            return

    await message.answer(
        "Доступно:\n"
        "/forbidden — показать стоп-лист\n"
        "/forbidden add strawberry — добавить продукт\n"
        "/forbidden remove strawberry — удалить продукт\n"
        "/forbidden clear — очистить стоп-лист"
    )


@dp.message(Command("plan"))
async def cmd_plan(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    container.ensure_default_schedule(user_id)

    now = datetime.now()
    current_day_name = now.strftime("%A").lower()
    current_time = now.strftime("%H:%M")
    target_day = now.strftime("%Y-%m-%d")

    result = container.orchestrator.run_daily_cycle(
        user_id=user_id,
        target_day=target_day,
        current_day_name=current_day_name,
        current_time=current_time,
    )

    if result["status"] != "ok":
        await message.answer(result["message"])
        return

    await message.answer(TelegramFormatter.format_meal_plan(result["meal_plan"]))
    await message.answer(TelegramFormatter.format_delivery_decision(result["delivery_decision"]))

    if result["order_plan"]:
        await message.answer(TelegramFormatter.format_order_plan(result["order_plan"]))

    if result["execution_result"]:
        await message.answer(TelegramFormatter.format_execution_result(result["execution_result"]))


@dp.message(Command("week"))
async def cmd_week(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")

    result = container.orchestrator.run_weekly_planning(
        user_id=user_id,
        start_date=start_date,
        days=7,
    )

    if result["status"] != "ok":
        await message.answer(result["message"])
        return

    await message.answer(TelegramFormatter.format_weekly_plans(result["plans"]))


async def main():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is empty in .env")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())