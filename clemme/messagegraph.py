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

def peoplegraph_to_data(messageids, messrels, peopleids): 
    print("simplifying graphdata")
    with open("boringppl.p", "rb") as infile:
        boringppl=pickle.load(infile)
    print(" - know boring people")
    def replaceguy(a):
        if a not in boringppl:
            return a
        else:
            return "boring"
    pplrels = [(replaceguy(messageids[a][0]), replaceguy(messageids[b][0]), 1) for (a,b) in messrels if b in messageids]
    print(" - simplified edges")
    pplreldict = {}
    for (a,b,w) in pplrels:
        if (a,b) in pplreldict:
            pplreldict[(a,b)]+=w
        else:
            pplreldict[(a,b)]=w
    pplrels = [(a,b,pplreldict[(a,b)]) for (a,b) in pplreldict]
    print(" - added weights")
    ppl = [g for g in peopleids if g not in boringppl]
    print(" - removed boring people")
    with open("pplgraphdata.p", "wb") as f:
        pickle.dump([pplrels, ppl],f)
    print(" - done")        

def peoplegraph_from_data(completelyconnected=False):
    with open("pplgraphdata.p", "rb") as f:
        pplrels, ppl = pickle.load(f)
    G=nx.DiGraph()
    G.add_node("boring")
    if completelyconnected:
        G.add_nodes_from(ppl)
        G.add_weighted_edges_from([(a,b,0.5) for a in G.nodes() for b in G.nodes()])#nondescript edges
    G.add_weighted_edges_from(pplrels)#ppl edges
    print("graph done. drawing {} nodes and {} edges.".format(len(G.nodes()), len(G.edges())))
    #colors by degree
    H=nx.Graph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from([(u,v) for (u,v,d) in G.edges(data=True) if d['weight']>1.5])
    G.remove_nodes_from([n for n in G.nodes() if H.degree(n)==0])
    print("max weight is {}".format(max([d['weight'] for (a,b,d) in G.edges(data=True)])))
    pos = nx.spring_layout(G, weight=None)
    with open("drawdata.p", "wb") as f:
        pickle.dump([pos,G,H],f)

def draw_peoplegraph(nodecolor='contacts', nodelabel='none', edgecolor='black'):
    plt.close()
    print("drawing nodecolor={}, label={}".format(nodecolor, nodelabel))
    with open("drawdata.p", "rb") as f:
        pos, G, H = pickle.load(f)
   #draw nodes
    if nodecolor=='contacts':
        cm = plt.get_cmap('rainbow')
        degreelist=[H.degree(node) for node in G.nodes() if node != "boring"]
        cNorm  = colors.Normalize(vmin=min(degreelist), vmax=max(degreelist))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        nx.draw_networkx_nodes(G,pos, nodelist=G.nodes(), node_color=scalarMap.to_rgba(degreelist), node_size=200)
    elif nodecolor == 'weightdegree':
        cm = plt.get_cmap('bwr')
        weightdeg=[G.in_degree(node, weight='weight')-G.out_degree(node, weight='weight') for node in G.nodes() if node !='boring']
        thresh=min([max(weightdeg), 0-min(weightdeg)])
        cNorm  = colors.Normalize(vmin=0-thresh, vmax=thresh)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        nx.draw_networkx_nodes(G,pos, nodelist=[n for n in G.nodes() if n !='boring'], node_color=scalarMap.to_rgba(weightdeg), node_size=200) 
    elif nodecolor == 'volume':
        cm = plt.get_cmap('bwr')
        weightdeg=[G.in_degree(node, weight='weight')+G.out_degree(node, weight='weight') for node in G.nodes() if node !='boring']
        thresh=max(weightdeg)
        thresh=1000
        cNorm  = colors.Normalize(vmin=0-thresh, vmax=thresh)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        nx.draw_networkx_nodes(G,pos, nodelist=[n for n in G.nodes() if n !='boring'], node_color=scalarMap.to_rgba(weightdeg), node_size=200) 
    elif nodecolor == 'outvolume':
        cm = plt.get_cmap('bwr')
        weightdeg=[G.out_degree(node, weight='weight') for node in G.nodes() if node !='boring']
        thresh=max(weightdeg)
        thresh=1000
        cNorm  = colors.Normalize(vmin=0-thresh, vmax=thresh)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        nx.draw_networkx_nodes(G,pos, nodelist=[n for n in G.nodes() if n !='boring'], node_color=scalarMap.to_rgba(weightdeg), node_size=200) 
    elif nodecolor=='jira':
        colorlist = list(map(lambda n: (1,0,0,1) if Idd[n]['email']=='jira@apache.org' else (0,0,1,1), G.nodes()))
        nx.draw_networkx_nodes(G,pos, nodelist=G.nodes(), node_color=colorlist, node_size=200)
    nx.draw_networkx_nodes(G,pos, nodelist=["boring"], node_color=(0,0,0,1), node_size=1000)
   #draw edges
    if edgecolor=='black':
        cm = plt.get_cmap('gray')
        cNorm  = colors.Normalize(vmax=100, vmin=0)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        drawedges = [(u,v, d) for (u,v,d) in G.edges(data=True) if d['weight']>0.9] 
#        drawweights = [d['weight'] for (u,v,d) in drawedges]
#        edgecol={(u,v,d):scalarMap.to_rgba(d['weight']) for (u,v,d) in drawedges} 
#        nx.draw_networkx_edges(G, pos, edgelist=drawedges, edge_color=scalarMap.to_rgba(drawweights))
        nx.draw_networkx_edges(G, pos, edgelist=drawedges)
   #draw labels
    if nodelabel=='name':
        labels={node:Idd[node]['name']+"\n"+Idd[node]['email'] for node in G.nodes() if node != 'boring'}
        nx.draw_networkx_labels(G,pos,labels,font_size=5)
    elif nodelabel=='degree':
        labels={node:G.in_degree(node, weight='weight')-G.out_degree(node, weight='weight') for node in G.nodes() if node != 'boring'}
        nx.draw_networkx_labels(G,pos,labels,font_size=8)
    elif nodelabel=='volume':
        labels={node:G.in_degree(node, weight='weight')+G.out_degree(node, weight='weight') for node in G.nodes() if node != 'boring'}
        for n in [n for n in labels if labels[n]>450]:
            print("   {} at {} has volume {}".format(Idd[n]['name'],Idd[n]['email'],labels[n]))
        nx.draw_networkx_labels(G,pos,labels,font_size=8)
    elif nodelabel=='outvolume':
        labels={node:G.out_degree(node, weight='weight') for node in G.nodes() if node != 'boring'}
        for n in [n for n in labels if labels[n]>450]:
            print("   {} at {} has outvolume {}".format(Idd[n]['name'],Idd[n]['email'],labels[n]))
        nx.draw_networkx_labels(G,pos,labels,font_size=8)
    elif nodelabel=='nameifdegree':
        degrees={node:G.in_degree(node, weight='weight')-G.out_degree(node, weight='weight') for node in G.nodes() if node != 'boring'}
        labels={node:Idd[node]['name']+"\n"+Idd[node]['email'] for node in degrees if degrees[node]**2>200**2}
        for n in labels:
            print("   {} at {} has degree {}".format(Idd[n]['name'],Idd[n]['email'],degrees[n]))
        nx.draw_networkx_labels(G,pos,labels,font_size=8)
  ##drawing
    plt.ylim([-0.1,1.1])
    plt.xlim([-0.1,1.1])
    plt.savefig("pplgraph_ncolor={}_lbl={}_edge={}.png".format(nodecolor, nodelabel, edgecolor))

def inspect_graphdata():
    with open("pplgraphdata.p", "rb") as f:
        pplrels, ppl = pickle.load(f)
    hist, bins = np.histogram([w for (a,b,w) in pplrels], bins=2000, density=True)
    widths = np.diff(bins)
    plt.bar(bins[:-1], hist, widths)
    plt.show() 
    

with open("messagedata_complete.p", 'rb') as infile:
    messageids, messrels, peopleids = pickle.load(infile)
with open("Iddict.p", 'rb') as infile:
    Idd=pickle.load(infile)
    Idd['boring']={'name':'boring', 'email':'boring'}
print("==== treating {} messages ====".format(len(messageids)))
#messagegraph(messageids, messrels, peopleids)
#peoplegraph_to_data(messageids, messrels, peopleids)
#peoplegraph_from_data()
for e in ['black', 'none']:
    draw_peoplegraph(nodecolor='outvolume', nodelabel='outvolume', edgecolor=e)
    draw_peoplegraph(nodecolor='volume', nodelabel='volume', edgecolor=e)
    draw_peoplegraph(nodecolor='jira', nodelabel='none', edgecolor=e)
    draw_peoplegraph(nodecolor='jira', nodelabel='name', edgecolor=e)
    draw_peoplegraph(nodecolor='weightdegree', nodelabel='nameifdegree', edgecolor=e)
    draw_peoplegraph(nodecolor='weightdegree', nodelabel='degree', edgecolor=e)
#inspect_graphdata()
