#local database stuff
import pymongo
from pymongo import MongoClient

import pandas as pd

import re

import networkx as nx

#auxiliary
import datetime
import pprint #pretty printing
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors


def messagegraph(messageids, messrels, peopleids):
    pplcolors = {guy:(np.random.uniform(), np.random.uniform(), np.random.uniform()) for guy in peopleids}
    authorrels = [(a,b) for a in messageids for b in messageids if messageids[a][0]==messageids[b][0]]
    #adding weights
    messrels = [(u,v, 10) for (u,v) in messrels]
    authorrels = [(u,v, 1) for (u,v) in authorrels]
    G=nx.DiGraph()
    G.add_nodes_from(messageids)
    G.add_weighted_edges_from([(u,v, 0.1) for u in G.nodes() for v in G.nodes()]) #adding nondescript edges for springs
    G.add_weighted_edges_from(authorrels) #adding people relations
    G.add_weighted_edges_from(messrels) #adding reply relations
    G.remove_nodes_from([mess for mess in G.nodes() if mess not in messageids])#remove unknown messages
    print("graph done. drawing.")
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos, nodelist=G.nodes(), node_color=[pplcolors[messageids[mess][0]] for mess in G.nodes()], node_size=20)
    nx.draw_networkx_edges(G, pos, edgelist=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight']==10])
#    nx.draw_networkx_edges(G, pos) #draw all edges
    plt.savefig("messagegraph.png")

def peoplegraph(messageids, messrels, peopleids): 
    pplrels = [(messageids[a][0], messageids[b][0], 10) for (a,b) in messrels if b in messageids]
    G=nx.DiGraph()
    G.add_nodes_from(peopleids)
    G.add_weighted_edges_from([(a,b,0.001) for a in G.nodes() for b in G.nodes()])#nondescript edges
    G.add_weighted_edges_from(pplrels)#ppl edges
    print("graph done. drawing.")
    #colors by degree
    cm = plt.get_cmap('OrRd')
    H=nx.DiGraph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from([(u,v) for (u,v,d) in G.edges(data=True) if d['weight']==10])
    G.remove_nodes_from([n for n in G.nodes() if H.degree(n)==0])
    degreelist=[H.degree(node) for node in G.nodes()]
    cNorm  = colors.Normalize(vmin=0, vmax=max(degreelist))
    cNorm  = colors.Normalize(vmin=0, vmax=10)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos, nodelist=G.nodes(), node_color=scalarMap.to_rgba(degreelist), node_size=20)
    nx.draw_networkx_edges(G, pos, edgelist=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight']==10])
#    nx.draw_networkx_edges(G, pos) #draw all edges
    plt.savefig("pplgraph.png")

with open("messagedata_10000.p", 'rb') as infile:
    messageids, messrels, peopleids = pickle.load(infile)
print("==== treating {} messages ====".format(len(messageids)))
#messagegraph(messageids, messrels, peopleids)
peoplegraph(messageids, messrels, peopleids)
