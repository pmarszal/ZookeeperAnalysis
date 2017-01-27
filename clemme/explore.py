#local database stuff
import pymongo
from pymongo import MongoClient

import pandas as pd

#auxiliary
import datetime
import pprint #pretty printing
import matplotlib.pyplot as plt
import numpy as np


#MAIN
print("starting")
client = MongoClient('localhost',27017) 
try:
    db = client['smartshark_test']
#    for current in db.collection_names():
#        print("NEW COLLECTION: {}".format(current))
#        print(" - count is {}".format(db[current].count()))
#        print(" - example is {}\n".format(db[current].find_one()))

    print(pd.DataFrame(list(db['hunk'].find())))
finally:
    client.close()
