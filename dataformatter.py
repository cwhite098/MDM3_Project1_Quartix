# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 21:18:44 2021

@author: kiera
"""
import numpy as np
import pandas as pd
import json
from tsfresh import extract_features
import ast

g = open('data/uncategorised.json',"r")
f = open('data/categorised.json',"r")
h = open("Data/unlinked.json","r")
    
g=json.loads(g.read())
    
g=json.dumps(g,sort_keys=True, indent=4)
g=g.replace("null","None")
h=json.loads(h.read())
    
h=json.dumps(h,sort_keys=True, indent=4)
h=h.replace("null","None")
    
    
    
    #'uncatogorized = json.dumps(uncatogorized, indent=4,sort_keys=True)
    #print(uncatogorized)
    
    
newfile = open(r"C:\Users\kiera\Desktop\categorized_data_reformated.txt","w")
newfile2 = open(r"C:\Users\kiera\Desktop\uncategorized_data_reformated.txt","w")
newfile3 = open(r"C:\Users\kiera\Desktop\unlinked_data_reformated.txt","w")
newfile.write(json.dumps(ast.literal_eval(f.read()), indent=4, sort_keys=True))
    #print(json.dumps(ast.literal_eval(g), indent=4, sort_keys=True))
    
    #print(json.dumps(ast.literal_eval(g.read()), indent=4, sort_keys=True))
newfile2.write(g)
newfile3.write(h)
newfile.close()
newfile2.close()
newfile3.close()