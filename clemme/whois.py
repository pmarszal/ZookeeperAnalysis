#local database stuff
import pymongo
from pymongo import MongoClient

import pandas as pd

import re

#auxiliary
import datetime
import pprint #pretty printing
import matplotlib.pyplot as plt
import numpy as np
import pickle


#MAIN

def toc(db):
# Check out collections
    for current in db.collection_names():
        print("NEW COLLECTION: {}".format(current))
        print(" - count is {}".format(db[current].count()))
        print(" - example is {}\n".format(db[current].find_one()))

def Idd(db):
    d={guy['_id']:guy for guy in db['people'].find()}
    print("identified {} people".format(len(d)))
    return d 
     
print("starting client")
client = MongoClient('localhost',27017) 
try:
    db = client['smartshark_test']
#    with open("Iddict.p", 'wb') as outfile:
#        pickle.dump(Idd(db), outfile)
    toc(db)   
finally:
    client.close()
