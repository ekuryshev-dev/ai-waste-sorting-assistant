#iterator
class WasteEventStream:

    def __init__(self, records): #save records, and put index 0
        self._records = records
        self._index = 0

    def __iter__(self): #return object, which can be use in loop `for`
        return self

    def __next__(self): #return next record
        if self._index >= len(self._records):
            raise StopIteration #inform that records finish

        record = self._records[self._index]
        self._index += 1

        return record

#yield
def generate_events(stream): #create the function which accepts a stream of records
    for record in stream: #go through the records one by one.
        yield record #it yields one record and pauses the generator's execution, preserving its state.
                    #The generator produces values sequentially.
