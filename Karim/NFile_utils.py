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

user_name = "utopia21"
password = "Qwerty123"
base_url = 'http://advancedapi.octoparse.com/'
token_entity = log_in(base_url, user_name, password)




client = Client(advanced_api=True)
r = client.refresh_token(token_entity['refresh_token'])
client.set_access_token(token_entity['access_token'])
r_tg = client.list_task_groups()['data']
tasks = client.list_group_tasks(r_tg[0]['taskGroupId'])
started = client.start_task(tasks["data"][0]["taskId"])

print(started)
Nfile1 = client.export_non_exported_data(tasks["data"][0]["taskId"], 1000)
first_extract = client.export_non_exported_data(tasks["data"][1]["taskId"], 1000)
second_extract = client.export_non_exported_data(tasks["data"][2]["taskId"], 1000)

#print("\nExported data:")
Nfile_df = pd.DataFrame(Nfile1['data']['dataList']).drop_duplicates()
first_extract_df = pd.DataFrame(first_extract['data']['dataList']).drop_duplicates()
second_extract_df = pd.DataFrame(second_extract['data']['dataList']).drop_duplicates()

#print(Nfile_df.drop_duplicates())
#print(first_extract_df.drop_duplicates())
#print(second_extract_df.drop_duplicates())




