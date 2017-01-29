import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import PCA
#auxiliary
import datetime
import pprint #pretty printing
import matplotlib.pyplot as plt
import numpy as np
import pickle


maxcount='all'
with open("clusterdata_{}.p".format(maxcount), 'rb') as infile:
    ppld=pickle.load(infile)
df = pd.DataFrame.from_dict(ppld, orient='index').fillna(0)
X = preprocessing.scale(df)

pca=PCA(n_components=2)
X_r=pca.fit(X).transform(X)


with open("Iddict.p", 'rb') as infile:
    Idd=pickle.load(infile)
for guy in Idd:
    if Idd[guy]['name']=='dev':
        print(Idd[guy])
    elif Idd[guy]['name'][0:2]=='zoo':
        print(Idd[guy])

index=list(df.index.values)
namelist = list(map(lambda guy: Idd[guy]['name'], index))
def guy_to_cat(guy):
    if Idd[guy]['email']=='jira@apache.org':
        return 1
    elif Idd[guy]['name']=='dev':
        return 2
    else:
        return 0
cat=list(map(guy_to_cat, index))

boringppl = [index[i] for i in range(0,len(index)) if X_r[i,0]**2+X_r[i,1]**2 <=5]
print("judged {} people boring".format(len(boringppl)))
pickle.dump(boringppl, open("boringppl.p", 'wb'))
#for i in range(0,len(index)):
#    if X_r[i,0]**2+X_r[i,1]**2 >5:
#        print("{} // {} is {}".format(X_r[i,0],X_r[i,1], Idd[index[i]]['name']+" "+Idd[index[i]]['email']))

plt.scatter(X_r[:,0], X_r[:,1],c=cat)
plt.show()

