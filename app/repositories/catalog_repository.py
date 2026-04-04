from typing import List
from app.models.meal import MealCandidate


class CatalogRepository:
    def __init__(self):
        self._catalog: List[MealCandidate] = []

    def get_catalog(self) -> List[MealCandidate]:
        return self._catalog

    def replace_catalog(self, items: List[MealCandidate]) -> None:
        self._catalog = items