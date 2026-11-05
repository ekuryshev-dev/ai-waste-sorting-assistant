from uuid import uuid4 #unique ID for every record
from datetime import datetime, timezone



class WasteRecord:

    def __init__(self, item, category, region_code,record_id=None, created_at=None):
        self._id =  record_id if record_id is not None else uuid4() #unique ID and save in object
        self._item = item #save name
        self._category = category #save category
        self._region_code = region_code #save region
        self._created_at = (
        created_at if created_at is not None
        else datetime.now(timezone.utc)) #save current date and time

#access methods
#Getters. A method that allows you to access an attribute in a given class
    def get_id(self): #obtaining an ID
        return self._id #returning an ID

    def get_item(self):
        return self._item

    def get_category(self):
        return self._category

    def get_region_code(self):
        return self._region_code

    def get_created_at(self):
        return self._created_at

#Setters. A method that allows you to set or mutate the value of an attribute in a class
# for _id no setter, because it´s unique and it´s can´t be change
# for _created_at no setter, because data and time must be saved and not change

    def set_item(self,item): #create method for change name, self - object which change, item - new inform
        self._item = item #save new inform inside object

    def set_category(self,category):
        self._category = category

    def set_region_code(self,region_code):
        self._region_code = region_code
