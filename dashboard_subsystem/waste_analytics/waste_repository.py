class WasteRepository:

    def __init__(self): #When a WasteRepository object is created, an empty list is initialized to store WasteRecord objects.
        self._records = []

    def add(self, record): #Adds a new entry to the list. This is a method that modifies the object's state (a mutator).
        self._records.append(record)

    def get_all(self): #Returns all saved records.
        return self._records.copy()

    def get_by_region(self, region_code): #The method iterates through the records, checks the region using a getter from WasteRecord, and returns only the matching objects.
        result = []

        for record in self._records:
            if record.get_region_code() == region_code:
                result.append(record)

        return result