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

def example_messages(db):
# Print some messages
    count = 1
    for obj in list(db['message'].find()):
        print(list(obj.keys()))
        print(obj)
        print("\n\n===\n\n")
        count+=1
        if count >3:
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
         #update messagedict
            try:
                messd[obj['_id']]={'from':obj['from_id'], 'tolist':obj['to_ids'], 'is_reply_to':obj['in_reply_to_id']}
            except KeyError:
                messd[obj['_id']]={'from':obj['from_id'], 'tolist':obj['to_ids'], 'is_reply_to':'None'}
         #update peopledict
           #update nbr_sent
            if obj['from_id'] not in ppld:
                ppld[obj['from_id']] = {}
            if 'nbr_sent' not in ppld[obj['from_id']]:
                ppld[obj['from_id']]['nbr_sent']=1
            else:
                ppld[obj['from_id']]['nbr_sent']+=1
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
                elif 'outcontactset' not in consd[guy]:
                    consd[guy]['outcontactset']=set([obj['from_id']])
                else:
                    consd[guy]['outcontactset'].add(obj['from_id'])

        except KeyError:
            pass
        count +=1
        if count>maxcount:
            break
    print(ppld)
    print(consd)
    #data for people: nbr messages sent, nbr people contacted, nbr messages rec, nbr people contacted by, nbr replies given, nbr deepreplies given, nbr replies gotten, nbr deepreplies gotten
#    peopledict={guy:{'nbr_sent':0,'nbr_rec':0,'nbr_outcontacts':0,'nbr_incontacts':0,'nbr_hasreplied:0','nbr_wasreplied':0 } for guy in peopleids}
#    contactsetdict={guy:{'incontactset'=set(), 'outcontactset'=set()} for guy in peopleids}
#    for mess in messagedict:
#        obj=messagedict[mess]
#        peopledict[obj['from']]['nbr_sent']+=1
#        contactset[obj['from']]['outcontactset'].update(obj['tolist'])
#        for toId in obj['tolist']:
#            peopledict[toId]['nbr_rec']+=1
        
    
#    with open("clusterdata_{}.p".format(maxcount), 'wb') as outfile:
#        pickle.dump([messagedict, peopledict], outfile)

print("starting")
client = MongoClient('localhost',27017) 
try:
    db = client['smartshark_test']
    clusterdata(db, 3)
finally:
    client.close()
