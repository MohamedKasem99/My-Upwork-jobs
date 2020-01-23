import csv 
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import numpy as np
import nltk
import itertools
from nltk.corpus import stopwords
nltk.download("stopwords")
nltk.download('punkt')

def pre_process_df_keywords(df):
    for column in df.columns:
        for indx, entry in enumerate(df[column].dropna(axis=0)):
            if len(entry.split()) > 0 and entry[-1] != " ":
                df[column][indx] = entry + " "
                
def pre_process(message):
    stopWords = set(stopwords.words('english'))
    pronouns = ["we", "We","WE","I","me","Me","ME","THEY","they","They","Them","them","THEM","YOU","You","you"]
    tabs = ["first", "parent second", ""]
    for word in message.split():
        if word not in stopWords and word not in pronouns:
            yield word
            #words.append(word)
    #yield dict(zip(words,np.zeros(len(words),dtype=np.int)))
    
def pre_process2(message):
    stopWords = set(stopwords.words('english'))
    pronouns = ["we", "We","WE","I","me","Me","ME","THEY","they","They","Them","them","THEM","YOU","You","you"]
    tabs = ["first", "parent second", ""]
    for word in message.split():
        if word not in stopWords and word not in pronouns:
            yield dict(word,[np.zeros(12),0])
    
def gen_len(iter):
    return sum([1 for _ in iter])


def isMatch_1_word(word1,word2,thresh=80): return (fuzz.ratio(word1, word2) > thresh)
def isMatch_many_words(word1,message,thresh=80): return (fuzz.partial_ratio(word1, message) > thresh)

def column_summary(word1, df):
    summary = np.zeros(len(df.columns))
    for col_indx, worker in enumerate(df.columns):
        c = 0
        for word2 in df[worker].dropna(axis=0):
            if isMatch_1_word(word1,word2):
                summary[col_indx]+=1
    return summary

def which_worker(message, first, bad_keywords):
    mat = []
    for word in pre_process(message):
        for bad_keyword in bad_keywords[bad_keywords.columns[0]]:

            if isMatch_1_word(word, bad_keyword):
                print(word, bad_keyword)
                print("BREAKING")
        mat.append(column_summary(word,first))
    return np.array(mat)