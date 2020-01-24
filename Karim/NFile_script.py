import smtplib, ssl
import run_api
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

pd = run_api.pd

port = 465  # For SSL
smtp_server = "smtp.gmail.com"

creds_file = pd.read_csv("email_creds_for_NFiles.csv")

sender_email = creds_file[creds_file.columns[0]].dropna(axis=0,how='all').values[0]
password = creds_file[creds_file.columns[1]].dropna(axis=0,how='all').values[0]
receivers = creds_file[creds_file.columns[2]].dropna(axis=0,how='all').values

def send_mail(title, link, from_, receivers):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        try:
            server.login(sender_email, password)
        except smtplib.SMTPAuthenticationError:
            print("""Couldn't login to your email. Here are possible fixes:
            1- Make sure you entered a correct email and password.
            2- Follow instructions to allow less secure apps on your account.""")
        else:
            for receiver_email in receivers:
                message = MIMEMultipart()
                message['To'] = receiver_email
                message['From'] = from_
                message['Subject'] = "Iron glove and fletcher"
                body = """Title: {}\nLink: {}""".format(title, link)
                message.attach(MIMEText(body, 'plain'))
                server.sendmail(sender_email, receiver_email, message.as_string())

for Nfile_index, Nfile_df in enumerate(run_api.Nfiles_df_list):
    try:
        for row in Nfile_df.itertuples():
            send_mail(row.field1_Text_Text, row.field1_Link_Link, sender_email, receivers)
    except:
        print(f"couldn't send Nfile{Nfile_index+1}")
        raise 
    