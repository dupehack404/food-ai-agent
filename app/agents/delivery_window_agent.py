from datetime import datetime
from app.models.user_profile import UserProfile, TimeWindow
from app.models.meal import MealPlan
from app.models.delivery import DeliveryDecision


class DeliveryWindowAgent:
    def decide(
        self,
        profile: UserProfile,
        meal_plan: MealPlan,
        current_day_name: str,
        current_time: str,
    ) -> DeliveryDecision:
        windows = getattr(profile.weekly_availability, current_day_name, [])

        if not windows:
            return DeliveryDecision(
                action="do_not_order",
                chosen_slot=None,
                reason=f"На {self._translate_day(current_day_name)} не настроены окна доставки.",
            )

        for window in windows:
            if self._is_time_in_window(current_time, window):
                return DeliveryDecision(
                    action="order_now",
                    chosen_slot=f"{window.start}-{window.end}",
                    reason="Сейчас можно безопасно оформить заказ.",
                )

        next_window = self._find_next_window_after_time(current_time, windows)
        if next_window:
            return DeliveryDecision(
                action="schedule_for_later",
                chosen_slot=f"{next_window.start}-{next_window.end}",
                reason=f"Сейчас не лучшее время для доставки. Ближайшее безопасное окно: {next_window.start}-{next_window.end}.",
            )

        return DeliveryDecision(
            action="do_not_order",
            chosen_slot=None,
            reason="На сегодня безопасных окон доставки больше нет.",
        )

    def _is_time_in_window(self, current_time: str, window: TimeWindow) -> bool:
        now = self._to_minutes(current_time)
        start = self._to_minutes(window.start)
        end = self._to_minutes(window.end)
        return start <= now <= end

    def _find_next_window_after_time(self, current_time: str, windows: list[TimeWindow]) -> TimeWindow | None:
        now = self._to_minutes(current_time)
        future_windows = [
            window for window in windows
            if self._to_minutes(window.start) > now
        ]
        if not future_windows:
            return None
        return sorted(future_windows, key=lambda w: self._to_minutes(w.start))[0]

    def _to_minutes(self, time_str: str) -> int:
        parsed = datetime.strptime(time_str, "%H:%M")
        return parsed.hour * 60 + parsed.minute

    def _translate_day(self, day_name: str) -> str:
        mapping = {
            "monday": "понедельник",
            "tuesday": "вторник",
            "wednesday": "среду",
            "thursday": "четверг",
            "friday": "пятницу",
            "saturday": "субботу",
            "sunday": "воскресенье",
        }
        return mapping.get(day_name, day_name)