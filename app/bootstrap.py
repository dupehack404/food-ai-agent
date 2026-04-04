from app.core.config import settings
from app.services.llm_service import LLMService
from app.services.playwright_executor import PlaywrightExecutor

from app.agents.preference_agent import PreferenceAgent
from app.agents.meal_agent import MealAgent
from app.agents.delivery_window_agent import DeliveryWindowAgent
from app.agents.order_agent import OrderAgent

from app.models.meal import MealCandidate
from app.models.user_profile import TimeWindow
from app.repositories.user_repository import UserRepository
from app.repositories.meal_history_repository import MealHistoryRepository
from app.repositories.catalog_repository import CatalogRepository
from app.orchestrator.food_orchestrator import FoodOrchestrator


class AppContainer:
    def __init__(self):
        self.llm_service = LLMService(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
        )

        self.user_repository = UserRepository()
        self.meal_history_repository = MealHistoryRepository()
        self.catalog_repository = CatalogRepository()

        self.preference_agent = PreferenceAgent()
        self.meal_agent = MealAgent()
        self.delivery_window_agent = DeliveryWindowAgent()
        self.order_agent = OrderAgent()
        self.order_executor = PlaywrightExecutor()

        self.orchestrator = FoodOrchestrator(
            user_repository=self.user_repository,
            meal_history_repository=self.meal_history_repository,
            catalog_repository=self.catalog_repository,
            preference_agent=self.preference_agent,
            meal_agent=self.meal_agent,
            delivery_window_agent=self.delivery_window_agent,
            order_agent=self.order_agent,
            order_executor=self.order_executor,
        )

    def seed_demo_catalog(self):
        if self.catalog_repository.get_catalog():
            return

        self.catalog_repository.replace_catalog([
    MealCandidate(
        id="meal-1",
        name="Chicken with rice",
        calories=650,
        price=350.0,
        ingredients=["chicken", "rice", "spices"],
        tags=["high_protein", "no_milk"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-2",
        name="Fish with potato",
        calories=700,
        price=420.0,
        ingredients=["fish", "potato", "oil"],
        tags=["omega3"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-3",
        name="Beef with buckwheat",
        calories=750,
        price=390.0,
        ingredients=["beef", "buckwheat", "salt"],
        tags=["high_protein"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-4",
        name="Omelette with cheese",
        calories=500,
        price=280.0,
        ingredients=["eggs", "cheese", "milk"],
        tags=["breakfast"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-5",
        name="Chicken salad",
        calories=550,
        price=330.0,
        ingredients=["chicken", "lettuce", "tomato"],
        tags=["light"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-6",
        name="Turkey with bulgur",
        calories=680,
        price=360.0,
        ingredients=["turkey", "bulgur", "spices"],
        tags=["high_protein"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-7",
        name="Chicken soup",
        calories=480,
        price=290.0,
        ingredients=["chicken", "broth", "potato", "carrot"],
        tags=["light"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-8",
        name="Beef with rice",
        calories=720,
        price=400.0,
        ingredients=["beef", "rice", "salt"],
        tags=["high_protein"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-9",
        name="Turkey salad",
        calories=530,
        price=320.0,
        ingredients=["turkey", "lettuce", "cucumber"],
        tags=["light"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-10",
        name="Lentil bowl",
        calories=610,
        price=280.0,
        ingredients=["lentils", "rice", "tomato"],
        tags=["vegan", "budget"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-11",
        name="Chicken with pasta",
        calories=700,
        price=340.0,
        ingredients=["chicken", "pasta", "spices"],
        tags=["high_protein"],
        source="demo_catalog",
        available=True,
    ),
    MealCandidate(
        id="meal-12",
        name="Beef stew",
        calories=690,
        price=410.0,
        ingredients=["beef", "potato", "carrot"],
        tags=["hot_meal"],
        source="demo_catalog",
        available=True,
    ),
])

    def ensure_default_schedule(self, user_id: str):
        profile = self.user_repository.get_user_profile(user_id)
        if not profile:
            return

        default_windows = {
            "monday": [
                TimeWindow(start="08:00", end="09:30"),
                TimeWindow(start="16:00", end="21:00"),
            ],
            "tuesday": [
                TimeWindow(start="08:00", end="09:30"),
                TimeWindow(start="16:00", end="21:00"),
            ],
            "wednesday": [
                TimeWindow(start="08:00", end="09:30"),
                TimeWindow(start="16:00", end="21:00"),
            ],
            "thursday": [
                TimeWindow(start="08:00", end="09:30"),
                TimeWindow(start="16:00", end="21:00"),
            ],
            "friday": [
                TimeWindow(start="08:00", end="09:30"),
                TimeWindow(start="16:00", end="21:00"),
            ],
            "saturday": [
                TimeWindow(start="10:00", end="21:00"),
            ],
            "sunday": [
                TimeWindow(start="10:00", end="21:00"),
            ],
        }

        changed = False

        for day, windows in default_windows.items():
            current_windows = getattr(profile.weekly_availability, day)
            if not current_windows:
                setattr(profile.weekly_availability, day, windows)
                changed = True

        if changed:
            self.user_repository.save_user_profile(profile)