#Processes the record for analytics. will be able to transmit a correct record for further processing by analytics.


from waste_analytics.stream_processor import StreamProcessor


class AnalyticsProcessor(StreamProcessor): #Inheritance. Create a subclass that inherits from Stream Processor.

    def __init__(self, repository): #Store the repository inside the object. This is Dependency Injection — pass in a ready-made dependency rather than creating it inside the class.
        self._repository = repository

    def process(self, record): #Abstract method wich hands data over for safekeeping
        self._repository.add(record)
        return record
