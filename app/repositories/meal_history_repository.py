import json
from pathlib import Path
from typing import List

from app.models.meal import MealPlan


class MealHistoryRepository:
    def __init__(self, file_path: str = "data/meal_history.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()
        self._storage: dict[str, list[MealPlan]] = self._load_storage()

    def _ensure_file(self) -> None:
        if not self.file_path.exists():
            self.file_path.write_text("{}", encoding="utf-8")

    def _load_storage(self) -> dict[str, list[MealPlan]]:
        raw_data = json.loads(self.file_path.read_text(encoding="utf-8"))
        result: dict[str, list[MealPlan]] = {}

        for user_id, plans in raw_data.items():
            result[user_id] = [MealPlan.model_validate(plan) for plan in plans]

        return result

    def _persist(self) -> None:
        raw_data = {
            user_id: [plan.model_dump() for plan in plans]
            for user_id, plans in self._storage.items()
        }
        self.file_path.write_text(
            json.dumps(raw_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_recent_meal_plans(self, user_id: str, limit: int = 7) -> List[MealPlan]:
        return self._storage.get(user_id, [])[-limit:]

    def save_meal_plan(self, user_id: str, meal_plan: MealPlan) -> None:
        self._storage.setdefault(user_id, []).append(meal_plan)
        self._persist()