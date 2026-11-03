class TrendPoint:
    def __init__(self, period, recyclable_count, compostable_count, landfill_count, unknown_count):
        self._period = period
        self._recyclable_count = recyclable_count
        self._compostable_count = compostable_count
        self._landfill_count = landfill_count
        self._unknown_count = unknown_count

    # Getters. A method that allows you to access an attribute in a given class
    def get_period(self):
        return self._period

    def get_recyclable_count(self):
        return self._recyclable_count

    def get_compostable_count(self):
        return self._compostable_count

    def get_landfill_count(self):
        return self._landfill_count

    def get_unknown_count(self):
        return self._unknown_count

    # Setters.  A method that allows you to set or mutate the value of an attribute in a class

    def set_period(self, period):
        self._period = period

    def set_recyclable_count(self, recyclable_count):
        self._recyclable_count = recyclable_count

    def set_compostable_count(self, compostable_count):
        self._compostable_count = compostable_count

    def set_landfill_count(self, landfill_count):
        self._landfill_count = landfill_count

    def set_unknown_count(self, unknown_count):
        self._unknown_count = unknown_count