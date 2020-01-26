from octoparse.client import Client
import requests 
import sys
import os
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


def clear_all_data(client, NFile_also=True):
    ID_dict = get_task_IDs(client)
    for ID in ID_dict["extracts_IDs"]:
        print(client.clear_data( ID ))
    if NFile_also:
        for ID in ID_dict["NFiles_IDs"]:
            print(client.clear_data( ID ))


if __name__ == "__main__":
    client = Client(advanced_api=True)  
    creds_file = pd.read_csv("octoparse_creds.csv")
    user_name = creds_file[creds_file.columns[0]].dropna(axis=0,how='all').values[0]
    password = creds_file[creds_file.columns[1]].dropna(axis=0,how='all').values[0]
    base_url = 'http://advancedapi.octoparse.com/'
    token_entity = log_in(base_url, user_name, password)

    ID_dict = get_task_IDs(client)
    clear_all_data(client, ID_dict)