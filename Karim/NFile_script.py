import run_api
from email_sender import send_mail

pd = run_api.pd

if __name__ == "__main__": 

    creds_file = pd.read_csv("email_creds_for_NFiles.csv")

    sender_email = creds_file[creds_file.columns[0]].dropna(axis=0,how='all').values[0]
    password = creds_file[creds_file.columns[1]].dropna(axis=0,how='all').values[0]
    receivers = creds_file[creds_file.columns[2]].dropna(axis=0,how='all').values

    for Nfile_index, Nfile_df in enumerate(run_api.Nfiles_df_list):
        try:
            for row in Nfile_df.itertuples():
                body = """Title: {}\nLink: {}""".format(row.field1_Text_Text, row.field1_Link_Link)
                for receiver in receivers:
                    send_mail("Iron glove and fletcher",body , sender_email, password, receiver)
        except:
            print(f"couldn't send Nfile{Nfile_index+1}")
            raise 
        