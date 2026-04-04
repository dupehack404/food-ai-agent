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
from app.repositories.catalog_repository import CatalogRepository
from app.orchestrator.food_orchestrator import FoodOrchestrator


def main():
    print("Project started successfully.")
    print("Model:", settings.OPENAI_MODEL)
    print("OpenAI key loaded:", bool(settings.OPENAI_API_KEY))

    llm_service = LLMService(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
    )
    print("LLM service initialized:", llm_service is not None)

    user_repo = UserRepository()
    catalog_repo = CatalogRepository()

    preference_agent = PreferenceAgent()
    meal_agent = MealAgent()
    delivery_window_agent = DeliveryWindowAgent()
    order_agent = OrderAgent()
    order_executor = PlaywrightExecutor()

    orchestrator = FoodOrchestrator(
        user_repository=user_repo,
        catalog_repository=catalog_repo,
        preference_agent=preference_agent,
        meal_agent=meal_agent,
        delivery_window_agent=delivery_window_agent,
        order_agent=order_agent,
        order_executor=order_executor,
    )

    user_message = (
        "У меня аллергия на milk, eggs. "
        "Не люблю fish и broccoli. "
        "Люблю chicken, rice. "
        "Мне нужно 2200 ккал."
    )

    profile = orchestrator.update_preferences(
        user_id="user-1",
        user_message=user_message,
    )

    profile.weekly_availability.monday = [
        TimeWindow(start="08:00", end="09:30"),
        TimeWindow(start="16:00", end="21:00"),
    ]
    profile.weekly_availability.tuesday = [
        TimeWindow(start="08:00", end="09:30"),
        TimeWindow(start="16:00", end="21:00"),
    ]
    profile.weekly_availability.wednesday = [
        TimeWindow(start="08:00", end="09:30"),
        TimeWindow(start="16:00", end="21:00"),
    ]
    profile.weekly_availability.thursday = [
        TimeWindow(start="08:00", end="09:30"),
        TimeWindow(start="16:00", end="21:00"),
    ]
    profile.weekly_availability.friday = [
        TimeWindow(start="08:00", end="09:30"),
        TimeWindow(start="16:00", end="21:00"),
    ]
    user_repo.save_user_profile(profile)

    catalog_repo.replace_catalog([
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
    ])

    result = orchestrator.run_daily_cycle(
        user_id="user-1",
        target_day="2026-04-04",
        current_day_name="monday",
        current_time="17:10",
    )

    print("Profile:", result["profile"].model_dump())
    print("Meal plan:", result["meal_plan"].model_dump())
    print("Delivery decision:", result["delivery_decision"].model_dump())

    if result["order_plan"]:
        print("Order plan:", result["order_plan"].model_dump())

    if result["execution_result"]:
        print("Execution result:", result["execution_result"].model_dump())


if __name__ == "__main__":
    main()