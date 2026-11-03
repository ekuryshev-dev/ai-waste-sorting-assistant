from enum import Enum


class Category(str,Enum):
    recyclable = "recyclable"
    compostable = "compostable"
    landfill = "landfill"
    unknown = "unknown"