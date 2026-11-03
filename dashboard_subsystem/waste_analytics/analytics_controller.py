
#Dependency Injection. Pass a ready-made object of another class via the constructor, instead of creating it inside the controller.
class AnalyticsController:
    def __init__(self,service):
        self._service = service

    def get_service(self):
        return self._service

    def set_service(self,service):
        self._service = service

    def get_statistics(self,region_code):
        records = self._service.get_records_by_region(region_code)
        summary = self._service.calculate_statistics(records)
        return summary

    def get_trends(self,region_code):
        records = self._service.get_records_by_region(region_code)
        trends = self._service.calculate_trends(records)
        return trends