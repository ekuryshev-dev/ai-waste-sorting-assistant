
class Dashboard:

    def __init__(self, controller, region_code):
        self._controller = controller
        self._region_code = region_code

    # Getters
    def get_controller(self):
        return self._controller

    def get_region_code(self):
        return self._region_code

    # Setters
    def set_controller(self, controller):
        self._controller = controller

    def set_region_code(self, region_code):
        self._region_code = region_code

    # Display general statistics
    def display_statistics(self):
        summary = self._controller.get_statistics(self._region_code)

        print("Region:", self._region_code)
        print("Total records:", summary.get_total_records())

    # Display category distribution
    def display_category_distribution(self):
        summary = self._controller.get_statistics(self._region_code)

        recyclable = summary.get_recyclable_percentage()
        compostable = summary.get_compostable_percentage()
        landfill = summary.get_landfill_percentage()

        if summary.get_total_records() > 0:
            unknown = 100 - recyclable - compostable - landfill
        else:
            unknown = 0.0

        print("Recyclable:", recyclable, "%")
        print("Compostable:", compostable, "%")
        print("Landfill:", landfill, "%")
        print("Unknown:", round(unknown, 2), "%")

    # Display recyclable share
    def display_recycling_rate(self):
        summary = self._controller.get_statistics(self._region_code)

        print("Recyclable share:", summary.get_recycling_rate(), "%")

    # Display trends
    def display_trends(self):
        trends = self._controller.get_trends(self._region_code)

        for point in trends:
            print("Date:", point.get_period())
            print("Recyclable:", point.get_recyclable_count())
            print("Compostable:", point.get_compostable_count())
            print("Landfill:", point.get_landfill_count())
            print("Unknown:", point.get_unknown_count())
