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
import sys


#MAIN

def toc(db):
# Check out collections
    for current in db.collection_names():
        print("NEW COLLECTION: {}".format(current))
        print(" - count is {}".format(db[current].count()))
        print(" - example is {}\n".format(db[current].find_one()))

def example_messages(db):
# Print some messages
    count = 1
    for obj in list(db['message'].find()):
        print(list(obj.keys()))
        print(obj)
        print("\n\n===\n\n")
        count+=1
        if count >10:
            break

def save_messrels(db, maxcount):
    messageids={} #_id:[author,subject]
    messrels=[] #(_id, replyto)
    peopleids=set()
    count=1
    for obj in list(db['message'].find()):
        try:
            print("'{}' is id {}".format(obj['subject'], obj['_id']))
            messageids[obj['_id']]=[obj['from_id'], obj['subject']]
            peopleids.update([obj['from_id']])
            print(" and in reply to {}".format(obj['in_reply_to_id']))
            messrels.append((obj['_id'], obj['in_reply_to_id']))
        except KeyError:
            pass
        count +=1
        if count>maxcount:
            break
    with open("messagedata_{}.p".format(maxcount), 'wb') as outfile:
        pickle.dump([messageids, messrels, peopleids], outfile)

def match_messages(db):
# RegEx match messages
    count=1
    p_response = re.compile('(AM|PM), "([^"]*)" <([^>]*)> wrote:')
    for obj in list(db['message'].find()):
        try:
            iterator=p_response.finditer(obj['body'])
            for match in iterator:
                print(match.groups())
        except KeyError:
            pass
        count+=1
        if count>10:
            break


def clusterdata(db, maxcount):
    #data for messages: fromId, toIds, replyId, 
    messd={}
    ppld={}
    consd={}
    count=1
    for obj in list(db['message'].find()):
        try:
            if 'from_id' not in obj:
                continue
         #update messagedict
            if 'in_reply_to_id' in obj:
                messd[obj['_id']]={'from':obj['from_id'], 'tolist':obj['to_ids'], 'is_reply_to':obj['in_reply_to_id']}
            else:
                messd[obj['_id']]={'from':obj['from_id'], 'tolist':obj['to_ids'], 'is_reply_to':'None'}
         #update peopledict
           #update nbr_sent & replies given
            if obj['from_id'] not in ppld:
                ppld[obj['from_id']] = {}
            if 'nbr_sent' not in ppld[obj['from_id']]:
                ppld[obj['from_id']]['nbr_sent']=1
            else:
                ppld[obj['from_id']]['nbr_sent']+=1
            if messd[obj['_id']]['is_reply_to'] != 'None':
                if 'reply_sent' not in ppld[obj['from_id']]:
                    ppld[obj['from_id']]['reply_sent']=1
                else:
                    ppld[obj['from_id']]['reply_sent']+=1
           #update nbr_rec
            for guy in obj['to_ids']:
                if guy  not in ppld:
                    ppld[guy] = {}
                if 'nbr_rec' not in ppld[guy]:
                    ppld[guy]['nbr_rec']=1
                else:
                    ppld[guy]['nbr_rec']+=1
                if messd[obj['_id']]['is_reply_to'] != 'None':
                    if 'reply_rec' not in ppld[guy]:
                        ppld[guy]['reply_rec']=1
                    else:
                        ppld[guy]['reply_rec']+=1
           #update outcontacts
            if obj['from_id'] not in consd:
                consd[obj['from_id']]={'outcontactset':set(obj['to_ids'])}
            elif 'outcontactset' not in consd[obj['from_id']]:
                consd[obj['from_id']]['outcontactset']=set(obj['to_ids'])
            else:
                consd[obj['from_id']]['outcontactset'].update(obj['to_ids'])
           #update intcontacts
            for guy in obj['to_ids']:
                if guy not in consd:
                    consd[guy]={'incontactset':set([obj['from_id']])}
                elif 'incontactset' not in consd[guy]:
                    consd[guy]['incontactset']=set([obj['from_id']])
                else:
                    consd[guy]['incontactset'].add(obj['from_id'])
        except KeyError:
            raise
        count +=1
        if maxcount != 'all':
            if count>maxcount:
                break
    for guy in consd:
        if 'incontactset' in consd[guy]:
            ppld[guy]['nbr_incontacts']=len(consd[guy]['incontactset'])
        else:
            ppld[guy]['nbr_incontacts']=0
        if 'outcontactset' in consd[guy]:
            ppld[guy]['nbr_outcontacts']=len(consd[guy]['outcontactset'])
        else:
            ppld[guy]['nbr_outcontacts']=0 
    
    with open("clusterdata_{}.p".format(maxcount), 'wb') as outfile:
        pickle.dump(ppld, outfile)

print("starting")
client = MongoClient('localhost',27017) 
try:
    db = client['smartshark_test']
    maxcount='all'
    example_messages(db)
    sys.exit()
    clusterdata(db, maxcount)
finally:
    client.close()

