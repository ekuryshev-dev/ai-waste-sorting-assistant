from waste_analytics.statistics_summary import StatisticsSummary
from waste_analytics.category import Category
from waste_analytics.trend_point import TrendPoint


class WasteAnalyticsService:

    def calculate_category_distribution(self, records): # Method for count the number of waste items in each category.
        counts = { #create a dictionary
            Category.recyclable: 0,
            Category.compostable: 0,
            Category.landfill: 0,
            Category.unknown: 0
        }

        for record in records: # Go through each record.
            category = record.get_category()
            if category in counts: # Check whether such a category exists in the dictionary.
                counts[category] += 1

        return counts

#using Dependency Injection
    def __init__(self, repository):
       self._repository = repository # the service will be able to access the data.
                                     #repository — a ready-to-use WasteRepository object passed to the service.
                                     # self._repository — store this object within WasteAnalyticsService.

    def get_repository(self):
        return self._repository

    def set_repository(self, repository):
        self._repository = repository

    def get_records_by_region(self, region_code):
        return self._repository.get_by_region(region_code)

    def calculate_recycling_rate(self,records):
      total = len(records) #returns the number of recognized objects.
      counts = self.calculate_category_distribution(records)
      recyclable = counts[Category.recyclable]

      if total != 0:
          result = (recyclable / total) * 100
      else:
          result = 0.0

      return result

    def calculate_statistics(self, records):
      total = len(records)
      counts = self.calculate_category_distribution(records)
      recycling_rate = self.calculate_recycling_rate(records)

      if total != 0:
        recyclable_percentage = (counts[Category.recyclable] / total) * 100
        compostable_percentage = (counts[Category.compostable] / total) * 100
        landfill_percentage = (counts[Category.landfill] / total) * 100
      else:
        recyclable_percentage = 0.0
        compostable_percentage = 0.0
        landfill_percentage = 0.0

      summary = StatisticsSummary (total, recyclable_percentage,
                 compostable_percentage, landfill_percentage,
                 recycling_rate)
      return summary

    def calculate_trends(self, records): # Method for calculating changes in the number of recognitions.
      trends = {} # empty dictionary for collect information by date

      for record in records:
          period = str(record.get_created_at().date()) # convert date to string.
          if period not in trends:
              trends[period] = {
                      Category.recyclable: 0,
                      Category.compostable: 0,
                      Category.landfill: 0,
                      Category.unknown: 0
              }

          category = record.get_category()
          if category in trends[period]:
              trends[period][category] += 1

      trends_point = [] #for save ready objects of "TrendPoint"
      for period in sorted(trends): #for go through the dates
          point = TrendPoint (period,
                              trends[period][Category.recyclable],
                              trends[period][Category.compostable],
                              trends[period][Category.landfill],
                              trends[period][Category.unknown])

          trends_point.append(point) #add every point in list

      return trends_point

