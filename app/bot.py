import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from app.core.config import settings
from app.bootstrap import AppContainer
from app.services.telegram_service import TelegramFormatter


container = AppContainer()
container.seed_demo_catalog()

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Бот запущен.\n\n"
        "Команды:\n"
        "/prefs <текст предпочтений>\n"
        "/profile\n"
        "/plan\n"
        "/week\n"
        "/help"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/prefs <текст> — обновить предпочтения\n"
        "/profile — показать профиль\n"
        "/plan — запустить дневной цикл\n"
        "/week — построить недельный план\n"
        "/help — показать помощь"
    )


@dp.message(Command("prefs"))
async def cmd_prefs(message: Message):
    user_id = str(message.from_user.id)

    raw_text = message.text or ""
    parts = raw_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "После /prefs передай текст.\n"
            "Пример:\n"
            "/prefs У меня аллергия на milk, eggs. Не люблю fish. Люблю chicken, rice. Мне нужно 2200 ккал. Бюджет 1200."
        )
        return

    user_message = parts[1]

    profile = container.orchestrator.update_preferences(
        user_id=user_id,
        user_message=user_message,
    )
    container.ensure_default_schedule(user_id)

    await message.answer("Предпочтения обновлены.")
    await message.answer(TelegramFormatter.format_profile(profile))


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = str(message.from_user.id)
    profile = container.user_repository.get_user_profile(user_id)

    if not profile:
        await message.answer("Профиль не найден. Сначала используй /prefs")
        return

    await message.answer(TelegramFormatter.format_profile(profile))


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