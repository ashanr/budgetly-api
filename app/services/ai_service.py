from datetime import date, datetime, timezone
from typing import Optional
import uuid
from app.services.analysis_service import AnalysisService
from app.services.budget_service import BudgetService
from app.core.config import get_settings
from app.schemas.ai import SpendingAnalysis, AIQueryResponse, DailyDigest, Alert

settings = get_settings()


class AIService:
    def __init__(self, analysis_service: AnalysisService, budget_service: BudgetService):
        self.analysis_service = analysis_service
        self.budget_service = budget_service

    async def analyze(self, user_id: str, start: date, end: date, include_recommendations: bool = True) -> SpendingAnalysis:
        data = await self.analysis_service.analyze_spending(user_id, start, end)

        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations(data)

        summary = self._generate_summary(data, start, end)

        return SpendingAnalysis(
            total_spent=data["total_spent"],
            by_category=data["by_category"],
            top_merchants=data["top_merchants"],
            recurring_total=data["recurring_total"],
            anomalies=data["anomalies"],
            summary=summary,
            recommendations=recommendations,
        )

    async def query(self, user_id: str, query: str, context: Optional[dict] = None) -> AIQueryResponse:
        answer, data = await self._process_query(user_id, query, context)

        return AIQueryResponse(
            query=query,
            answer=answer,
            data=data,
            confidence=0.85 if data else 0.5,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_daily_digest(self, user_id: str) -> DailyDigest:
        today = date.today()
        start_of_month = today.replace(day=1)

        today_data = await self.analysis_service.analyze_spending(user_id, today, today)
        month_data = await self.analysis_service.analyze_spending(user_id, start_of_month, today)
        budget_health = await self.budget_service.get_budget_health(user_id)
        budget_alerts = await self.budget_service.get_alerts(user_id)

        top_category = max(month_data["by_category"], key=month_data["by_category"].get) if month_data["by_category"] else None

        insights = []
        if month_data["total_spent"] > 0:
            insights.append(f"You have spent {month_data['total_spent']:.2f} this month.")
        if today_data["total_spent"] > 0:
            insights.append(f"Today's spending: {today_data['total_spent']:.2f}")
        if month_data["anomalies"]:
            insights.append(f"Detected {len(month_data['anomalies'])} unusual transaction(s) this month.")

        alerts = [
            Alert(
                alert_id=str(uuid.uuid4()),
                type=a["type"],
                severity=a["severity"],
                title=a["budget_name"],
                message=a["message"],
                created_at=datetime.now(timezone.utc),
            )
            for a in budget_alerts
        ]

        return DailyDigest(
            date=str(today),
            total_spent_today=today_data["total_spent"],
            total_spent_month=month_data["total_spent"],
            budget_status=[{"id": h.budget_id, "name": h.name, "status": h.status, "utilization": h.utilization_percent} for h in budget_health],
            top_category=top_category,
            insights=insights,
            alerts=alerts,
        )

    async def get_alerts(self, user_id: str) -> list[Alert]:
        raw_alerts = await self.budget_service.get_alerts(user_id)
        return [
            Alert(
                alert_id=str(uuid.uuid4()),
                type=a["type"],
                severity=a["severity"],
                title=a["budget_name"],
                message=a["message"],
                created_at=datetime.now(timezone.utc),
            )
            for a in raw_alerts
        ]

    async def get_recommendations(self, user_id: str) -> list[str]:
        today = date.today()
        start = today.replace(day=1)
        data = await self.analysis_service.analyze_spending(user_id, start, today)
        return self._generate_recommendations(data)

    def _generate_summary(self, data: dict, start: date, end: date) -> str:
        total = data["total_spent"]
        count = data["expense_count"]
        if count == 0:
            return f"No expenses recorded between {start} and {end}."
        top_cat = max(data["by_category"], key=data["by_category"].get) if data["by_category"] else "N/A"
        return f"Between {start} and {end}, you spent {total:.2f} across {count} transactions. Your highest spending category was {top_cat}."

    def _generate_recommendations(self, data: dict) -> list[str]:
        recs = []
        if data["recurring_total"] > data["total_spent"] * 0.5:
            recs.append("Over 50% of your spending is on recurring items. Review subscriptions for potential savings.")
        if data["anomalies"]:
            recs.append(f"You have {len(data['anomalies'])} unusually large transaction(s). Review them to ensure accuracy.")
        if not data["by_category"]:
            recs.append("Start categorizing your expenses to get better insights.")
        if data["total_spent"] > 0:
            recs.append("Track your expenses consistently to improve forecast accuracy.")
        return recs

    async def _process_query(self, user_id: str, query: str, context: Optional[dict]) -> tuple[str, Optional[dict]]:
        query_lower = query.lower()
        today = date.today()
        start_of_month = today.replace(day=1)

        if "this month" in query_lower or "monthly" in query_lower:
            data = await self.analysis_service.analyze_spending(user_id, start_of_month, today)
            if "how much" in query_lower or "spent" in query_lower:
                return f"You have spent {data['total_spent']:.2f} this month.", data
            if "category" in query_lower or "biggest" in query_lower:
                if data["by_category"]:
                    top = max(data["by_category"], key=data["by_category"].get)
                    return f"Your biggest spending category this month is {top} with {data['by_category'][top]:.2f}.", data

        if "on track" in query_lower or "budget" in query_lower:
            health = await self.budget_service.get_budget_health(user_id)
            over = [h for h in health if h.is_over_budget]
            if not health:
                return "You have no budgets set up yet. Create budgets to track your spending goals.", None
            if over:
                return f"You are over budget on {len(over)} budget(s). Review your spending.", {"over_budget": [h.name for h in over]}
            return "You are on track with your budgets!", {"budgets": len(health)}

        if "biggest expense" in query_lower or "largest" in query_lower:
            data = await self.analysis_service.analyze_spending(user_id, start_of_month, today)
            if data["by_category"]:
                top = max(data["by_category"], key=data["by_category"].get)
                return f"Your biggest expense category is {top} at {data['by_category'][top]:.2f}.", data

        return "I can help you analyze your spending. Try asking about this month's spending, your biggest expense, or whether you're on track with your budget.", None
