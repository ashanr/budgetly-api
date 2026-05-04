from app.services.budget_service import BudgetService
from app.services.analysis_service import AnalysisService


class NotificationService:
    def __init__(self, budget_service: BudgetService, analysis_service: AnalysisService):
        self.budget_service = budget_service
        self.analysis_service = analysis_service

    async def get_notifications(self, user_id: str) -> list[dict]:
        alerts = await self.budget_service.get_alerts(user_id)
        notifications = []

        for alert in alerts:
            notifications.append({
                "type": alert["type"],
                "severity": alert["severity"],
                "title": f"Budget Alert: {alert['budget_name']}",
                "message": alert["message"],
                "channel": "in_app",
            })

        return notifications
