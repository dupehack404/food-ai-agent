from app.models.user_profile import UserProfile
from app.models.meal import MealPlan
from app.models.delivery import DeliveryDecision
from app.models.order import OrderPlan, OrderExecutionResult


class TelegramFormatter:
    @staticmethod
    def format_profile(profile: UserProfile) -> str:
        return (
            f"Профиль:\n"
            f"user_id: {profile.user_id}\n"
            f"allergies: {', '.join(profile.allergies) or '-'}\n"
            f"dislikes: {', '.join(profile.dislikes) or '-'}\n"
            f"likes: {', '.join(profile.likes) or '-'}\n"
            f"forbidden: {', '.join(profile.forbidden_products) or '-'}\n"
            f"calorie_target: {profile.calorie_target}\n"
            f"daily_meal_count: {profile.daily_meal_count}\n"
            f"budget_per_day: {profile.budget_per_day if profile.budget_per_day is not None else '-'}"
        )

    @staticmethod
    def format_meal_plan(meal_plan: MealPlan) -> str:
        lines = [f"Meal plan на {meal_plan.day}:"]
        for meal in meal_plan.meals:
            lines.append(
                f"- {meal.meal_type}: {meal.item_name} "
                f"({meal.calories} kcal, {meal.price} RUB, score={meal.score})"
            )
            if meal.reason:
                lines.append(f"  reason: {meal.reason}")
        lines.append(f"Итого калории: {meal_plan.total_calories}")
        lines.append(f"Итого цена: {meal_plan.total_price}")
        return "\n".join(lines)

    @staticmethod
    def format_weekly_plans(plans: list[MealPlan]) -> str:
        lines = ["Недельный план:"]
        for plan in plans:
            items = ", ".join(meal.item_name for meal in plan.meals)
            lines.append(
                f"- {plan.day}: {items} | kcal={plan.total_calories} | price={plan.total_price}"
            )
        return "\n".join(lines)

    @staticmethod
    def format_delivery_decision(decision: DeliveryDecision) -> str:
        return (
            f"Delivery decision:\n"
            f"action: {decision.action}\n"
            f"slot: {decision.chosen_slot or '-'}\n"
            f"reason: {decision.reason}"
        )

    @staticmethod
    def format_order_plan(order_plan: OrderPlan) -> str:
        lines = [
            "Order plan:",
            f"provider: {order_plan.provider}",
            f"slot: {order_plan.delivery_slot or '-'}",
        ]
        for item in order_plan.items:
            lines.append(f"- {item.name} x{item.quantity}")
        lines.append(f"estimated price: {order_plan.total_estimated_price}")
        return "\n".join(lines)

    @staticmethod
    def format_execution_result(result: OrderExecutionResult) -> str:
        return (
            f"Execution result:\n"
            f"status: {result.status}\n"
            f"order_id: {result.order_id or '-'}\n"
            f"provider: {result.provider or '-'}\n"
            f"final_price: {result.final_price or '-'}\n"
            f"delivery_eta: {result.delivery_eta or '-'}\n"
            f"message: {result.message}"
        )