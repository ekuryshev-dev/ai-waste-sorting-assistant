#check the record that the entry specifies the item, category, and region.


from waste_analytics.stream_processor import StreamProcessor
from waste_analytics.waste_record import WasteRecord
from waste_analytics.category import Category


class ValidationProcessor(StreamProcessor):

    def process(self, record):

        if not isinstance(record, WasteRecord): #Verify that what we have been passed is indeed an object of the WasteRecord class.
            raise TypeError("Expected a WasteRecord")

        if not isinstance(record.get_item(), str) or not record.get_item().strip():
            raise ValueError("Item name cannot be empty")

        if not isinstance(record.get_region_code(), str) or not record.get_region_code().strip():
            raise ValueError("Region code cannot be empty")

        try:
            Category(record.get_category())
        except ValueError:
            raise ValueError("Invalid waste category")

        return record


