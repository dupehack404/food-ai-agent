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