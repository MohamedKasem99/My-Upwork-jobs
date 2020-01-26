import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

port = 465  # For SSL
smtp_server = "smtp.gmail.com"


def send_mail(subject, body, from_, password, receiver):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        try:
            server.login(from_, password)
        except smtplib.SMTPAuthenticationError:
            print("""Couldn't login to your email. Here are possible fixes:
            1- Make sure you entered a correct email and password.
            2- Follow instructions to allow less secure apps on your account.""")
        else:
            message = MIMEMultipart()
            message['To'] = receiver
            message['From'] = from_
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            server.sendmail(from_, receiver, message.as_string())