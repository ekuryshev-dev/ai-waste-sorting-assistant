#a common interface for data processors. Abstract class
from abc import ABC, abstractmethod


class StreamProcessor(ABC):

    @abstractmethod #Indicates that specific subclasses must implement the process() method.
    def process(self, record): #declare a method for processing a single record.
        pass

    def __or__(self, other): #This is a special Python method that allows to redefine the behavior of an operator `|´.
                            #self is the first handler (validation), and other is the second (analytics).
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        return AnalyticsPipeline(self, other)


class AnalyticsPipeline(StreamProcessor):

    def __init__(self, first, second): #save two handlers inside Pipeline
        self._first = first
        self._second = second

    def process(self, record):
        result = self._first.process(record)
        return self._second.process(result)
