from datetime import datetime, timedelta


class FoodOrchestrator:
    def __init__(
        self,
        user_repository,
        meal_history_repository,
        catalog_repository,
        preference_agent,
        meal_agent,
        delivery_window_agent,
        order_agent,
        order_executor,
    ):
        self.user_repository = user_repository
        self.meal_history_repository = meal_history_repository
        self.catalog_repository = catalog_repository
        self.preference_agent = preference_agent
        self.meal_agent = meal_agent
        self.delivery_window_agent = delivery_window_agent
        self.order_agent = order_agent
        self.order_executor = order_executor

    def update_preferences(self, user_id: str, user_message: str):
        current_profile = self.user_repository.get_user_profile(user_id)

        updated_profile = self.preference_agent.update_profile(
            user_id=user_id,
            current_profile=current_profile,
            user_message=user_message,
        )

        self.user_repository.save_user_profile(updated_profile)
        return updated_profile

    def update_dislike_mode(self, user_id: str, mode: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        if mode not in {"soft", "hard"}:
            return None

        profile.dislike_mode = mode
        self.user_repository.save_user_profile(profile)
        return profile

    def update_calorie_target(self, user_id: str, calories: int):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        profile.calorie_target = calories
        self.user_repository.save_user_profile(profile)
        return profile

    def update_daily_meal_count(self, user_id: str, meal_count: int):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        profile.daily_meal_count = meal_count
        self.user_repository.save_user_profile(profile)
        return profile

    def update_budget(self, user_id: str, budget: float | None):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        profile.budget_per_day = budget
        self.user_repository.save_user_profile(profile)
        return profile

    def add_forbidden_product(self, user_id: str, product: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        normalized = product.strip().lower()
        if normalized and normalized not in [x.lower() for x in profile.forbidden_products]:
            profile.forbidden_products.append(normalized)

        self.user_repository.save_user_profile(profile)
        return profile

    def remove_forbidden_product(self, user_id: str, product: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        normalized = product.strip().lower()
        profile.forbidden_products = [
            item for item in profile.forbidden_products
            if item.lower() != normalized
        ]

        self.user_repository.save_user_profile(profile)
        return profile

    def clear_forbidden_products(self, user_id: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        profile.forbidden_products = []
        self.user_repository.save_user_profile(profile)
        return profile

    def get_catalog(self):
        return self.catalog_repository.get_catalog()

    def get_safe_catalog(self, user_id: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        catalog = self.catalog_repository.get_catalog()
        return self.meal_agent.get_safe_catalog(profile, catalog)

    def set_day_schedule(self, user_id: str, day_name: str, windows: list):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        setattr(profile.weekly_availability, day_name, windows)
        self.user_repository.save_user_profile(profile)
        return profile

    def clear_day_schedule(self, user_id: str, day_name: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return None

        setattr(profile.weekly_availability, day_name, [])
        self.user_repository.save_user_profile(profile)
        return profile

    def run_daily_cycle(
        self,
        user_id: str,
        target_day: str,
        current_day_name: str,
        current_time: str,
    ):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return {
                "status": "error",
                "message": "User profile not found.",
            }

        catalog = self.catalog_repository.get_catalog()
        history = self.meal_history_repository.get_recent_meal_plans(user_id)

        meal_plan = self.meal_agent.plan(
            profile=profile,
            catalog=catalog,
            history=history,
            target_day=target_day,
        )

        delivery_decision = self.delivery_window_agent.decide(
            profile=profile,
            meal_plan=meal_plan,
            current_day_name=current_day_name,
            current_time=current_time,
        )

        result = {
            "status": "ok",
            "profile": profile,
            "history": history,
            "meal_plan": meal_plan,
            "delivery_decision": delivery_decision,
            "order_plan": None,
            "execution_result": None,
        }

        self.meal_history_repository.save_meal_plan(user_id, meal_plan)

        if delivery_decision.action == "order_now":
            order_plan = self.order_agent.build_order(
                profile=profile,
                meal_plan=meal_plan,
                chosen_slot=delivery_decision.chosen_slot,
            )
            execution_result = self.order_executor.execute(order_plan)

            result["order_plan"] = order_plan
            result["execution_result"] = execution_result

        return result

    def run_weekly_planning(self, user_id: str, start_date: str, days: int = 7):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return {
                "status": "error",
                "message": "User profile not found.",
            }

        catalog = self.catalog_repository.get_catalog()
        base_history = self.meal_history_repository.get_recent_meal_plans(user_id)

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        simulated_history = list(base_history)
        weekly_plans = []

        for offset in range(days):
            day_dt = start_dt + timedelta(days=offset)
            target_day = day_dt.strftime("%Y-%m-%d")

            meal_plan = self.meal_agent.plan(
                profile=profile,
                catalog=catalog,
                history=simulated_history,
                target_day=target_day,
            )

            weekly_plans.append(meal_plan)
            simulated_history.append(meal_plan)

        return {
            "status": "ok",
            "profile": profile,
            "plans": weekly_plans,
        }