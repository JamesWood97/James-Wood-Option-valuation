from knomial import *
from finitedifference import *

def get_value(question:str, return_as_float = True):
    while True:
        value = input(question)
        try:
            if return_as_float:
                return float(value)
            else:
                return int(value)
        except ValueError:
            print("Invalid number")

print(get_value("test",True))