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
print("starting")
client = MongoClient('localhost',27017) 
try:
    db = client['smartshark_test']
#    for current in db.collection_names():
#        print("NEW COLLECTION: {}".format(current))
#        print(" - count is {}".format(db[current].count()))
#        print(" - example is {}\n".format(db[current].find_one()))

#    print(pd.DataFrame(list(db['hunk'].find())))


    count = 1
    for obj in list(db['message'].find()):
        print(list(obj.keys()))
        print(obj)
        print("\n\n===\n\n")
        count+=1
        if count >3:
            break

    messageids={} #_id:[author,subject]
    messrels=[] #(_id, replyto)
    peopleids=[]

    count=1
    for obj in list(db['message'].find()):
        try:
            print("'{}' is id {}".format(obj['subject'], obj['_id']))
            messageids[obj['_id']]=[obj['from_id'], obj['subject']]
            peopleids.append(obj['from_id'])
            print(" and in reply to {}".format(obj['in_reply_to_id']))
            messrels.append((obj['_id'], obj['in_reply_to_id']))
        except KeyError:
            pass
        count +=1
        if count>1000:
            break
    with open("messagedata.p", 'wb') as outfile:
        pickle.dump([messageids, messrels, peopleids], outfile)

#    count=1
#    p_response = re.compile('(AM|PM), "([^"]*)" <([^>]*)> wrote:')
#    for obj in list(db['message'].find()):
#        try:
#            iterator=p_response.finditer(obj['body'])
#            for match in iterator:
#                print(match.groups())
#        except KeyError:
#            pass
#        count+=1
#        if count>10:
#            break
finally:
    client.close()
