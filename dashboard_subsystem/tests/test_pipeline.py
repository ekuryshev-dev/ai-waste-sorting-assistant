
import pytest

from waste_analytics.waste_repository import WasteRepository
from waste_analytics.waste_record import WasteRecord
from waste_analytics.category import Category
from waste_analytics.validation_processor import ValidationProcessor
from waste_analytics.analytics_processor import AnalyticsProcessor
from waste_analytics.waste_event_stream import WasteEventStream, generate_events


def test_invalid_record_not_saved():
    repository = WasteRepository()

    pipeline = ValidationProcessor() | AnalyticsProcessor(repository)

    record = WasteRecord(
        "",
        Category.recyclable,
        "Dortmund"
    )

    with pytest.raises(ValueError): #Checking the exception
        pipeline.process(record)

    assert len(repository.get_all()) == 0 #check repository

    #check iterator

def test_event_stream():
        records = [
            WasteRecord("Bottle", Category.recyclable, "Dortmund"),
            WasteRecord("Paper", Category.recyclable, "Dortmund")
        ]

        stream = WasteEventStream(records)

        first = next(stream)
        second = next(stream)

        assert first.get_item() == "Bottle"
        assert second.get_item() == "Paper"

        with pytest.raises(StopIteration):
            next(stream)

    #check generator and pipeline

def test_pipeline_with_generator():
        repository = WasteRepository()

        pipeline = ValidationProcessor() | AnalyticsProcessor(repository)

        records = [
            WasteRecord("Bottle", Category.recyclable, "Dortmund"),
            WasteRecord("Banana peel", Category.compostable, "Dortmund"),
            WasteRecord("Diaper", Category.landfill, "Herne")
        ]

        stream = WasteEventStream(records)

        for record in generate_events(stream):
            pipeline.process(record)

        saved_records = repository.get_all()

        assert len(saved_records) == 3
        assert saved_records[0].get_item() == "Bottle"
        assert saved_records[1].get_item() == "Banana peel"
        assert saved_records[2].get_item() == "Diaper"

