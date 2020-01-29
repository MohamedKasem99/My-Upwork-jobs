from octoparse.client import Client
import requests 
import sys
import os
import getpass
import pandas as pd


def log_in(base_url, username, password): 	
        """login and get a access token
        
        Arguments:
                base_url {string} -- authrization base url(currently same with api)
                username {[type]} -- your username
                password {[type]} -- your password
        
        Returns:
                json -- token entity include expiration and refresh token info like:
                        {
                                "access_token": "ABCD1234",      # Access permission
                                "token_type": "bearer",		 # Token type
                                "expires_in": 86399,		 # Access Token Expiration time (in seconds)(It is recommended to use the same token repeatedly within this time frame.) 
                                "refresh_token": "refresh_token" # To refresh Access Token
                        }
        """
        content = 'username={0}&password={1}&grant_type=password'.format(username, password)
        token_entity = requests.post(base_url + 'token', data = content).json()

        if 'access_token' in token_entity:
                print('Obtained my token successfully!')
                #print(token_entity)
                return token_entity
        else:
                print(token_entity['error_description'])
                os._exit(-2)


def append_non_exported(file_name, df_non_exported):
    df_exported = pd.read_csv(file_name)
    return df_exported.append(df_non_exported, ignore_index = True, sort= False).drop_duplicates().dropna()


def cleanup_df(df, subset):
    return df.drop_duplicates(subset=subset, keep="first").dropna().reset_index().drop('index',axis=1)


def start_task_by_ID(ID):
    started_status =  client.start_task(ID)
    print(started_status)
    return started_status


def get_task_IDs(client):
    num_extracts = 3
    r = client.refresh_token(token_entity['refresh_token'])
    client.set_access_token(token_entity['access_token'])
    
    r_tg = client.list_task_groups()['data']
    tasks = client.list_group_tasks(r_tg[0]['taskGroupId'])
    extracts_IDs = [0] * num_extracts
    NFiles_IDs = []
    others = []
    for i in tasks["data"]:
        if "firstextract" in i.values():
            extracts_IDs[0] = ((list(i.values())[0]))
        elif "secondextract" in i.values():
            extracts_IDs[1] = ((list(i.values())[0]))
        elif "thridextract" in i.values():      #this is misspelled in octoparse. DON'T CORRECT IT
            extracts_IDs[2] = ((list(i.values())[0]))
        elif "Nfile" in str((list(i.values())[1])):
            NFiles_IDs.append((list(i.values())[0]))
        else:
            others.append((list(i.values())[0]))
            
    return {"extracts_IDs": extracts_IDs,
    "NFiles_IDs": NFiles_IDs,
    "others": others}

def start_all_tasks(client, ID_dict):
    
    for ID in ID_dict["extracts_IDs"]:
        start_task_by_ID( ID )
    for ID in ID_dict["NFiles_IDs"]:
        start_task_by_ID( ID )
    

def clear_all_data(ID_dict, NFile_also=True):
    for ID in ID_dict["extracts_IDs"]:
        print(client.clear_data( ID ))
    if NFile_also:
        for ID in ID_dict["NFiles_IDs"]:
            print(client.clear_data( ID ))


def export_all_tasks_dfs(ID_dict, return_dict = False):
    """
        returns: a tuple of data frames (Nfiles_df, first_extract_df, second_extract_df)
        Nfiles_df -> is a list of Nfile data_frames
        
        returns: dictionary of data_frames for all extracts if return_dict is True (default = False)
        result = {
        "Nfiles_df": Nfiles_df
        "first_extract": first_extract_df
        "second_extract": second_extract_df
        }
    """
    NFiles_IDs = ID_dict["NFiles_IDs"]
    extracts_IDs = ID_dict["extracts_IDs"]
    others = ID_dict["others"]
 

    Nfiles_non_exported = [client.export_non_exported_data(Nfile, 1000) for Nfile in NFiles_IDs]

    first_extract_non_exported = client.export_non_exported_data(extracts_IDs[0], 1000)
    second_extract_non_exported = client.export_non_exported_data(extracts_IDs[1], 1000)
    third_extract_non_exported = client.export_non_exported_data(extracts_IDs[2], 1000)

    try:
        Nfiles_df_list = [pd.DataFrame(Nfile['data']['dataList']).drop_duplicates() for Nfile in Nfiles_non_exported]
    except:
        print("NFiles Not exported, Could be empty or a problem with octoparse. Considered empty for now")     
        Nfiles_df_list = [pd.DataFrame(columns= ["field1_Text_Text","field1_Link_Link"])]


    try:
        first_extract_df = pd.DataFrame(first_extract_non_exported['data']['dataList'])
    except:
        print("firstextract Not exported, Could be empty or a problem with octoparse. Considered empty for now")  
        first_extract_df = pd.DataFrame(columns= ["field1_Text_Text","field1_Link_Link"])
    

    try:
        second_extract_df = pd.DataFrame(second_extract_non_exported['data']['dataList'])
    except:
        print("secondextract Not exported, Could be empty or a problem with octoparse. Considered empty for now")  
        second_extract_df = pd.DataFrame(columns= ["field1","field2","field3"])


    try:
        third_extract_df = pd.DataFrame(third_extract_non_exported['data']['dataList'])
    except:
        print("thirdextract Not exported, Could be empty or a problem with octoparse. Considered empty for now")  
        third_extract_df = pd.DataFrame(columns= ["field1","email"])

    
    
    return {
        "Nfiles_df": Nfiles_df_list,
        "first_extract": first_extract_df,
        "second_extract": second_extract_df,
        "third_extract": third_extract_df
    } if return_dict else ( [cleanup_df(Nfile, "field1_Text_Text") for Nfile in Nfiles_df_list], cleanup_df(first_extract_df, "field1_Text_Text"), 
                           cleanup_df(second_extract_df, "field1")  , cleanup_df(third_extract_df, "field1") )




client = Client(advanced_api=True)  

creds_file = pd.read_csv("octoparse_creds.csv")
user_name = creds_file[creds_file.columns[0]].dropna(axis=0,how='all').values[0]
password = creds_file[creds_file.columns[1]].dropna(axis=0,how='all').values[0]

base_url = 'http://advancedapi.octoparse.com/'
token_entity = log_in(base_url, user_name.strip(), password.strip())

ID_dict = get_task_IDs(client)

start_all_tasks(client, ID_dict)

Nfiles_df_list, first_extract_df, second_extract_df, third_extract_df = export_all_tasks_dfs(ID_dict)

first_extract_df.to_csv("firstextract.csv", index = False)
second_extract_df.to_csv("secondextract.csv", index = False)
third_extract_df.to_csv("thirdextract.csv", index = False)
[Nfile.to_csv(f"NFile{num+1}.csv",index=False) for num, Nfile in enumerate(Nfiles_df_list) ]
