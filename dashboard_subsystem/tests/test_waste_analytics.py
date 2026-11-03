
from waste_analytics.category import Category
from waste_analytics.waste_record import WasteRecord
from waste_analytics.waste_repository import WasteRepository
from waste_analytics.waste_analytics_service import WasteAnalyticsService
from waste_analytics.analytics_controller import AnalyticsController


def create_test_data():
    repository = WasteRepository()

    repository.add(WasteRecord("Bottle", Category.recyclable, "Dortmund"))
    repository.add(WasteRecord("Paper", Category.recyclable, "Dortmund"))
    repository.add(WasteRecord("Banana peel", Category.compostable, "Dortmund"))
    repository.add(WasteRecord("Diaper", Category.landfill, "Herne"))
    repository.add(WasteRecord("Unknown item", Category.unknown, "Dortmund"))

    service = WasteAnalyticsService(repository)
    controller = AnalyticsController(service)

    return repository, service, controller


def test_category_distribution():
    repository, service, controller = create_test_data()

    records = repository.get_all()
    counts = service.calculate_category_distribution(records)

    assert counts[Category.recyclable] == 2
    assert counts[Category.compostable] == 1
    assert counts[Category.landfill] == 1
    assert counts[Category.unknown] == 1


def test_statistics():
    repository, service, controller = create_test_data()

    summary = service.calculate_statistics(repository.get_all())

    assert summary.get_total_records() == 5
    assert summary.get_recyclable_percentage() == 40.0
    assert summary.get_compostable_percentage() == 20.0
    assert summary.get_landfill_percentage() == 20.0
    assert summary.get_recycling_rate() == 40.0


def test_region_filtering():
    repository, service, controller = create_test_data()

    dortmund = controller.get_statistics("Dortmund")
    herne = controller.get_statistics("Herne")

    assert dortmund.get_total_records() == 4
    assert herne.get_total_records() == 1


def test_trends():
    repository, service, controller = create_test_data()

    trends = controller.get_trends("Dortmund")

    assert sum(p.get_recyclable_count() for p in trends) == 2
    assert sum(p.get_compostable_count() for p in trends) == 1
    assert sum(p.get_landfill_count() for p in trends) == 0
    assert sum(p.get_unknown_count() for p in trends) == 1


def test_empty_data():
    repository = WasteRepository()
    service = WasteAnalyticsService(repository)

    summary = service.calculate_statistics([])
    trends = service.calculate_trends([])

    assert summary.get_total_records() == 0
    assert summary.get_recycling_rate() == 0.0
    assert trends == []
