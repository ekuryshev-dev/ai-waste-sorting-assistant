from waste_analytics.category import Category
from waste_analytics.waste_record import WasteRecord
from waste_analytics.waste_repository import WasteRepository
from waste_analytics.waste_analytics_service import WasteAnalyticsService
from waste_analytics.analytics_controller import AnalyticsController
from waste_analytics.dashboard import Dashboard


def main():
    repository = WasteRepository()

    repository.add(WasteRecord("Bottle", Category.recyclable, "Dortmund"))

    service = WasteAnalyticsService(repository)
    controller = AnalyticsController(service)

    dashboard = Dashboard(controller, "Dortmund")

    print("\nWASTE ANALYTICS DASHBOARD")
    dashboard.display_statistics()
    dashboard.display_category_distribution()
    dashboard.display_recycling_rate()
    dashboard.display_trends()


if __name__ == "__main__":
    main()