class StatisticsSummary:
    def __init__(self, total_records, recyclable_percentage,
                 compostable_percentage, landfill_percentage,
                 recycling_rate):
        self._total_records = total_records
        self._recyclable_percentage = recyclable_percentage
        self._compostable_percentage = compostable_percentage
        self._landfill_percentage = landfill_percentage
        self._recycling_rate = recycling_rate

#Getters. A method that allows you to access an attribute in a given class
    def get_total_records(self):
            return self._total_records

    def get_recyclable_percentage(self):
            return self._recyclable_percentage

    def get_compostable_percentage(self):
            return self._compostable_percentage

    def get_landfill_percentage(self):
            return self._landfill_percentage

    def get_recycling_rate(self):
            return self._recycling_rate

#Setters.  A method that allows you to set or mutate the value of an attribute in a class
    def set_total_records(self, total_records):
            self._total_records = total_records

    def set_recyclable_percentage(self, recyclable_percentage):
            self._recyclable_percentage = recyclable_percentage

    def set_compostable_percentage(self, compostable_percentage):
            self._compostable_percentage = compostable_percentage

    def set_landfill_percentage(self, landfill_percentage):
            self._landfill_percentage = landfill_percentage

    def set_recycling_rate(self, recycling_rate):
            self._recycling_rate = recycling_rate