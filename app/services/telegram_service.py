from app.models.user_profile import UserProfile
from app.models.meal import MealPlan
from app.models.delivery import DeliveryDecision
from app.models.order import OrderPlan, OrderExecutionResult


class TelegramFormatter:
    @staticmethod
    def format_profile(profile: UserProfile) -> str:
        mode_label = "жёсткий" if profile.dislike_mode == "hard" else "мягкий"

        return (
            "📌 Профиль пользователя\n\n"
            f"ID: {profile.user_id}\n"
            f"Аллергии: {', '.join(profile.allergies) or '—'}\n"
            f"Нежелательные продукты: {', '.join(profile.dislikes) or '—'}\n"
            f"Любимые продукты: {', '.join(profile.likes) or '—'}\n"
            f"Жёстко запрещено: {', '.join(profile.forbidden_products) or '—'}\n"
            f"Цель по калориям: {profile.calorie_target}\n"
            f"Приёмов пищи в день: {profile.daily_meal_count}\n"
            f"Бюджет в день: {profile.budget_per_day if profile.budget_per_day is not None else '—'}\n"
            f"Режим dislikes: {mode_label}"
        )

    @staticmethod
    def format_meal_plan(meal_plan: MealPlan) -> str:
        lines = [f"🍽 План питания на {meal_plan.day}\n"]
        for idx, meal in enumerate(meal_plan.meals, start=1):
            lines.append(
                f"{idx}. {meal.meal_type}: {meal.item_name}\n"
                f"   • {meal.calories} ккал\n"
                f"   • {meal.price} ₽\n"
                f"   • score: {meal.score}"
            )
            if meal.reason:
                lines.append(f"   • причина выбора: {meal.reason}")
            lines.append("")
        lines.append(f"Итого калории: {meal_plan.total_calories}")
        lines.append(f"Итого цена: {meal_plan.total_price} ₽")
        return "\n".join(lines)

    @staticmethod
    def format_weekly_plans(plans: list[MealPlan]) -> str:
        lines = ["📅 Недельный план\n"]
        for plan in plans:
            items = ", ".join(meal.item_name for meal in plan.meals)
            lines.append(
                f"{plan.day}\n"
                f"   • блюда: {items}\n"
                f"   • калории: {plan.total_calories}\n"
                f"   • цена: {plan.total_price} ₽\n"
            )
        return "\n".join(lines)

    @staticmethod
    def format_delivery_decision(decision: DeliveryDecision) -> str:
        action_map = {
            "order_now": "заказывать сейчас",
            "schedule_for_later": "отложить на позже",
            "do_not_order": "не заказывать сейчас",
        }

        return (
            "🚚 Решение по доставке\n\n"
            f"Статус: {action_map.get(decision.action, decision.action)}\n"
            f"Слот: {decision.chosen_slot or '—'}\n"
            f"Причина: {decision.reason}"
        )

    @staticmethod
    def format_order_plan(order_plan: OrderPlan) -> str:
        lines = [
            "🛒 План заказа\n",
            f"Провайдер: {order_plan.provider}",
            f"Слот доставки: {order_plan.delivery_slot or '—'}",
            "",
            "Позиции:",
        ]
        for item in order_plan.items:
            lines.append(f"- {item.name} x{item.quantity}")
        lines.append("")
        lines.append(f"Оценочная стоимость: {order_plan.total_estimated_price} ₽")
        return "\n".join(lines)

    @staticmethod
    def format_execution_result(result: OrderExecutionResult) -> str:
        status_map = {
            "success": "успешно",
            "failed": "ошибка",
            "partial": "частично выполнено",
        }

        return (
            "✅ Результат выполнения\n\n"
            f"Статус: {status_map.get(result.status, result.status)}\n"
            f"ID заказа: {result.order_id or '—'}\n"
            f"Провайдер: {result.provider or '—'}\n"
            f"Итоговая цена: {result.final_price or '—'}\n"
            f"ETA / слот: {result.delivery_eta or '—'}\n"
            f"Комментарий: {result.message}"
        )