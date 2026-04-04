import re
from typing import Optional

from app.models.user_profile import (
    UserProfile,
    WeeklyAvailability,
    DeliveryPolicy,
)


class PreferenceAgent:
    def update_profile(
        self,
        user_id: str,
        current_profile: Optional[UserProfile],
        user_message: str,
    ) -> UserProfile:
        profile = current_profile or UserProfile(
            user_id=user_id,
            calorie_target=2000,
            weekly_availability=WeeklyAvailability(),
            delivery_policy=DeliveryPolicy(),
        )

        text = user_message.lower()

        allergies = self._extract_list(text, [
            "аллергия на",
            "allergy to",
        ])
        dislikes = self._extract_list(text, [
            "не люблю",
            "не ем",
            "don't like",
            "dislike",
        ])
        likes = self._extract_likes(text)
        forbidden = self._extract_list(text, [
            "запрещено",
            "нельзя",
            "forbidden",
            "avoid",
        ])

        calories = self._extract_calories(text)
        budget = self._extract_budget(text)

        if allergies:
            profile.allergies = self._merge_unique(profile.allergies, allergies)
        if dislikes:
            profile.dislikes = self._merge_unique(profile.dislikes, dislikes)
        if likes:
            profile.likes = self._merge_unique(profile.likes, likes)
        if forbidden:
            profile.forbidden_products = self._merge_unique(profile.forbidden_products, forbidden)
        if calories is not None:
            profile.calorie_target = calories
        if budget is not None:
            profile.budget_per_day = budget

        return profile

    def _extract_calories(self, text: str) -> Optional[int]:
        patterns = [
            r"(\d{3,4})\s*ккал",
            r"(\d{3,4})\s*kcal",
            r"калории\s*(\d{3,4})",
            r"calories\s*(\d{3,4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return None

    def _extract_budget(self, text: str) -> Optional[float]:
        patterns = [
            r"бюджет\s*(\d+(?:[.,]\d+)?)",
            r"до\s*(\d+(?:[.,]\d+)?)\s*(?:руб|₽|ruble|rub)",
            r"budget\s*(\d+(?:[.,]\d+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1).replace(",", "."))
        return None

    def _extract_likes(self, text: str) -> list[str]:
        patterns = [
            r"(?:^|[.!?\n]\s*)люблю\s+([^.!?\n]+)",
            r"(?:^|[.!?\n]\s*)нравится\s+([^.!?\n]+)",
            r"(?:^|[.!?\n]\s*)i like\s+([^.!?\n]+)",
            r"(?:^|[.!?\n]\s*)like\s+([^.!?\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                part = match.group(1)
                items = re.split(r",| и | and ", part)
                cleaned = [item.strip(" :-").lower() for item in items if item.strip()]
                return [item for item in cleaned if item]
        return []

    def _extract_list(self, text: str, triggers: list[str]) -> list[str]:
        for trigger in triggers:
            if trigger in text:
                part = text.split(trigger, 1)[1]
                part = re.split(r"[.!?\n]", part)[0]
                items = re.split(r",| и | and ", part)
                cleaned = [item.strip(" :-").lower() for item in items if item.strip()]
                return [item for item in cleaned if item]
        return []

    def _merge_unique(self, old: list[str], new: list[str]) -> list[str]:
        result = list(old)
        existing = set(x.lower() for x in old)
        for item in new:
            if item.lower() not in existing:
                result.append(item)
                existing.add(item.lower())
        return result