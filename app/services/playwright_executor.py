from app.models.order import OrderPlan, OrderExecutionResult


class PlaywrightExecutor:
    def execute(self, order_plan: OrderPlan) -> OrderExecutionResult:
        return OrderExecutionResult(
            status="success",
            order_id="demo-order-001",
            provider=order_plan.provider,
            final_price=order_plan.total_estimated_price,
            delivery_eta=order_plan.delivery_slot,
            message="Mock execution completed successfully.",
        )