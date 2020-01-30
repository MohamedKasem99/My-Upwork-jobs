import run_api
from email_sender import send_mail
from utils import compare_against_sent
pd = run_api.pd

if __name__ == "__main__": 

    creds_file = pd.read_csv("email_creds_for_NFiles.csv")

    sender_email = creds_file[creds_file.columns[0]].dropna(axis=0,how='all').values[0].strip()
    password = creds_file[creds_file.columns[1]].dropna(axis=0,how='all').values[0].strip()
    receivers = creds_file[creds_file.columns[2]].dropna(axis=0,how='all').values

    for Nfile_index, Nfile_df in enumerate(run_api.Nfiles_df_list):
        try:
            file_name = f"sent_Nfile{Nfile_index+1}.csv"

            try:
                Nfiles_sent = pd.read_csv(file_name)

            except: 
                Nfiles_sent = pd.DataFrame(columns = ["text&link"])
                Nfiles_sent.to_csv(file_name, index = False)


            for text, link in zip(Nfile_df["field1_Text_Text"], Nfile_df["field1_Link_Link"]):

                if text + link  in Nfiles_sent.values:
                    print("Breaking because already sent")
                    continue
                else: 
                    Nfiles_sent = pd.DataFrame(Nfiles_sent['text&link'].append(pd.Series(text+link), ignore_index=True), columns = ["text&link"])
                    Nfiles_sent.to_csv(file_name, index=False)

                body = """Title: {}\nLink: {}""".format(text, link)
                for receiver in receivers:
                    send_mail("Iron glove and fletcher",body , sender_email, password, receiver)
            
        except:
            print(f"couldn't send Nfile{Nfile_index+1}")
            raise 
        