
from waste_analytics.waste_repository import WasteRepository
from waste_analytics.waste_record import WasteRecord
from waste_analytics.category import Category
from waste_analytics.validation_processor import ValidationProcessor
from waste_analytics.analytics_processor import AnalyticsProcessor
from waste_analytics.waste_event_stream import WasteEventStream, generate_events


def main():
    repository = WasteRepository()

    pipeline = ValidationProcessor() | AnalyticsProcessor(repository)

    records = [
        WasteRecord("Plastic bottle", Category.recyclable, "Dortmund"),
        WasteRecord("Banana peel", Category.compostable, "Dortmund"),
        WasteRecord("Diaper", Category.landfill, "Herne"),
        WasteRecord("Unknown object", Category.unknown, "Dortmund")
    ]

    stream = WasteEventStream(records) #create iterator

    for record in generate_events(stream): #start generator
        pipeline.process(record) #start pipeline
        print("Processed:", record.get_item())

    print("Total records:", len(repository.get_all()))


if __name__ == "__main__":
    main()
