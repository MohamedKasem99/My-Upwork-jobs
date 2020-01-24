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
                
                
def start_task_by_ID(ID):
    started_status =  client.start_task(ID)
    print(started_status)
    return started_status

def start_all_tasks(client):
    r = client.refresh_token(token_entity['refresh_token'])
    client.set_access_token(token_entity['access_token'])
    
    r_tg = client.list_task_groups()['data']
    tasks = client.list_group_tasks(r_tg[0]['taskGroupId'])
    
    extracts_IDs = []
    NFiles_IDs = []
    for i in tasks["data"]:
        if "firstextract" in i.values() or "secondextract" in i.values():
            extracts_IDs.append((list(i.values())[0]))
        if "Nfile" in str((list(i.values())[1])):
            NFiles_IDs.append((list(i.values())[0]))
    
    for ID in extracts_IDs:
        start_task_by_ID( ID )
    for ID in NFiles_IDs:
        start_task_by_ID( ID )
    
    return {"extracts_IDs": extracts_IDs,
           "NFiles_IDs": NFiles_IDs}


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
    
    
    Nfiles_exported = [client.export_non_exported_data(Nfile, 1000) for Nfile in NFiles_IDs]
    
    first_extract = client.export_non_exported_data(extracts_IDs[0], 1000)
    second_extract = client.export_non_exported_data(extracts_IDs[1], 1000)

    #print("\nExported data:")
    Nfiles_df_list = [pd.DataFrame(Nfile['data']['dataList']).drop_duplicates() for Nfile in Nfiles_exported]
    
    first_extract_df = pd.DataFrame(first_extract['data']['dataList'])
    second_extract_df = pd.DataFrame(second_extract['data']['dataList'])
    
    return {
        "Nfiles_df": Nfiles_df,
        "first_extract": first_extract_df,
        "second_extract": second_extract_df
    } if return_dict else (Nfiles_df_list, first_extract_df, second_extract_df)




client = Client(advanced_api=True)  

creds_file = pd.read_csv("octoparse_creds.csv")
user_name = creds_file[creds_file.columns[0]].dropna(axis=0,how='all').values[0]
password = creds_file[creds_file.columns[1]].dropna(axis=0,how='all').values[0]

base_url = 'http://advancedapi.octoparse.com/'
token_entity = log_in(base_url, user_name, password)

ID_dict = start_all_tasks(client)

Nfiles_df_list, first_extract_df, second_extract_df = export_all_tasks_dfs(ID_dict)





