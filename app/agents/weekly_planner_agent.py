from datetime import datetime, timedelta

from app.models.user_profile import UserProfile
from app.models.meal import MealPlan, MealCandidate


class WeeklyPlannerAgent:
    def __init__(self, meal_agent):
        self.meal_agent = meal_agent

    def plan_week(
        self,
        profile: UserProfile,
        catalog: list[MealCandidate],
        history: list[MealPlan],
        start_date: str,
        days: int = 7,
    ) -> list[MealPlan]:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        simulated_history = list(history)
        weekly_plans: list[MealPlan] = []

        for offset in range(days):
            day_dt = start_dt + timedelta(days=offset)
            target_day = day_dt.strftime("%Y-%m-%d")

            day_plan = self.meal_agent.plan(
                profile=profile,
                catalog=catalog,
                history=simulated_history,
                target_day=target_day,
            )

            weekly_plans.append(day_plan)
            simulated_history.append(day_plan)

        return weekly_plans