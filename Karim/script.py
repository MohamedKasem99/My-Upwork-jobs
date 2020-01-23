import smtplib, ssl
import NFile_script
import time 
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


port = 465  # For SSL
smtp_server = "smtp.gmail.com"

sender_email = "kasem.personal@gmail.com"  # Enter your address
receivers = ["Karimafilal@hotmail.com"]  # Enter receiver address

#uncomment to have password hidden when entered.
#password = getpass("Type your password and press enter: ")
password = "Vsauce47Qualcomm"


def send_mail(subject, link, from_, to):
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
                body = """This link is from Nfile1: {}""".format(link)
                message.attach(MIMEText(body, 'plain'))
                server.sendmail(sender_email, receiver_email, message.as_string())

for row in NFile_script.Nfile_df.itertuples():
    send_mail(row.field1_Text_Text, row.field1_Link_Link, sender_email, receivers)

