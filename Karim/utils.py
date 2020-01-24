import csv 
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
import numpy as np
import nltk
import itertools
from nltk.corpus import stopwords
nltk.download("stopwords")
nltk.download('punkt')


def pre_process_df_keywords(df):
    for column in df.columns:
        for indx, entry in enumerate(df[column].dropna(axis=0)):
            if len(entry.split()) > 1 and entry[-1] != " ":
                df[column][indx] = entry + " "
def get_two_word(message):
    combined_2_words = []
    for word1, word2 in zip(message,list( message[1:] + list((message[0])))):
        combined_2_words.append(word1 + ' ' + word2)
    return combined_2_words

def pre_process(message):
    stopWords = set(stopwords.words('english'))
    pronouns = ["we", "We","WE","I","me","Me","ME","THEY","they","They","Them","them","THEM","YOU","You","you"]
    result = []
    for word in message.split():
        if word not in stopWords and word not in pronouns:
            result.append(word)
    return (result)
    
def gen_len(iter):
    return sum([1 for _ in iter])


def isMatch_1_word(word1,word2,thresh=80): return (fuzz.QRatio(word1, word2) > thresh)
def isMatch_many_words(word1,message,thresh=90): return (fuzz.partial_ratio(word1, message) >= thresh)

def column_summary(word1, df):
    summary = np.zeros(len(df.columns))
    for col_indx, worker in enumerate(df.columns):
        for word2 in df[worker].dropna(axis=0):
            if isMatch_1_word(word1,word2):
                summary[col_indx]+=1
    return summary


def summarize_one_words(message, first):
    mat = np.zeros((len(message),len(first.columns)))
    for word_indx, word in enumerate(message):    
        mat[word_indx]=(column_summary(word,first)) 
    return mat

def summarize_two_words(message, df):
    mat = np.zeros((len(message),len(df.columns)))
    for col_indx, worker in enumerate(df.columns):
        two_words = df[df[worker].apply(lambda x: len(str(x).split())>1)][worker]
        for word in two_words.dropna(axis=0):
            for word_indx, two_word in enumerate(get_two_word(message)):
                if isMatch_many_words(word, two_word):
                    mat[word_indx][col_indx]+=1
    return mat

def find_workers(raw_message, message, first, at_least_another = pd.DataFrame([0])):
    mat = summarize_one_words(message, first) + summarize_two_words(message, first)
    #print(mat,"\n\n")
    for word_indx, row_word in enumerate(mat[:]):
        if row_word.sum() == 0:
            mat[word_indx] = np.zeros((len(first.columns))); continue
            
        if len(first.columns[row_word != 0]) > 1:
            mat[word_indx] = np.zeros((len(first.columns)))
        
        if any([isMatch_1_word( message[word_indx], key_word ) for key_word in at_least_another[at_least_another.columns[0]] ]):
            mat[word_indx] = np.zeros((len(first.columns)))
    
    summary = np.array(mat).sum(axis=0)
    match_worker = first.columns[summary!=0].values
    summary_wo_zeros = summary[np.argwhere(summary).reshape(-1,1)]
    
    highest_match = ""
    #print(mat)
    #print(summary)
    #print(f"""He is looking for >>> {match_worker}""")

    if len(list(summary_wo_zeros)) != 0:
        if summary_wo_zeros.max() != summary_wo_zeros.min():
            highest_match = first.columns[np.argmax(summary)]
    return match_worker, highest_match

def step_1(raw_message, message, bad_keywords):
    matched_words = []
    hard_coded = ['class a ', 'class b ', 'class c ']
    one_words = bad_keywords[bad_keywords['name'].apply(lambda x: not len(x.split())>1)]["name"]
    two_words = bad_keywords[bad_keywords['name'].apply(lambda x: len(x.split())>1)]["name"]
    
    for word in hard_coded: 
        if word in raw_message.lower(): matched_words.append(word)
    for word in pre_process(raw_message):
        if any([isMatch_1_word(word, word2, thresh=85) for word2 in one_words]): matched_words.append(word)
    for word in two_words:
        if any([isMatch_many_words(word, two_word) for two_word in message]): matched_words.append(word)
    
    return matched_words


def append_sapces(text):
    if text.find("-"): 
        (text[:text.find("-")] + " " + text[text.find("-")] + " " + text[text.find("-")+1:])
    if text.find("/"):
        (text[:text.find("/")] + " " + text[text.find("/")] + " " + text[text.find("/")+1:])
    return text

def find_matching_key_word(message, df):
    results = []
    for key_word in df[df.columns[0]]:
        if any([isMatch_1_word(word,key_word) for word in message]):
            results.append(key_word)
        if any([isMatch_many_words(key_word, two_word) for two_word in get_two_word(message)]):
            results.append(key_word)
    return results

def extract_pay_info(second_extract, extractor):
    extracted_pay = pd.DataFrame({"field": second_extract['field3'].values, 
              "Res": list(map(extractor.extract_entities_dict,(map(append_sapces,second_extract['field3'].values)))),
              "Decesion": [" "] * len(second_extract['field3'].values)
             })
    for indx, item in enumerate(extracted_pay["Res"]):
        if len(item) != '' and ("money" in item.keys() or 'cardinal' in item.keys()):
            temp = re.findall(r'\d+', str(item.values()).replace(',',""))
            try:
                extracted_pay.iloc[indx]['Decesion'] = min(list(map(int, temp)))
            except:
                extracted_pay.iloc[indx]['Decesion'] = -1
        else:
            extracted_pay.iloc[indx]['Decesion'] = -1
    hard_coded_words = ["hour", "hr", "hourly", "day","daily","month","year"]
    hard_coded_delims= ["per", " a ", " an ", "/", "for"]
    amount = []
    
    for msg, pay_amount in zip(extracted_pay["field"], extracted_pay["Decesion"]):
        found = "NA"
        for key_word in hard_coded_words:
            if key_word in msg.lower():
                found = key_word 
        if found == "NA":
            for delim in hard_coded_delims:
                if msg.lower().find(delim) != -1:
                    found = (msg[msg.lower().find(delim)+ len(delim):])
        amount.append(found)
    extracted_pay = extracted_pay.reset_index().merge(pd.DataFrame({"amount":amount}).reset_index(), on="index",how="right").drop(["index"],axis=1)
    return extracted_pay