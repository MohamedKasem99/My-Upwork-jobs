import smtplib, ssl
import RPi.GPIO as GPIO
import time 
from getpass import getpass

port = 465  # For SSL
smtp_server = "smtp.gmail.com"

sender_email = "YOUR EMAIL"  # Enter your address
receivers = ["EMAIL1@gmail.com" , "EMAIL2@gmail.com" , "EMAIL3@gmail.com"]  # Enter receiver address

#uncomment to have password hidden when entered.
#password = getpass("Type your password and press enter: ")
password = "YOUR PASSWORD"


message = """\
Subject: Test

Start writing here: There has to be an empty line between subject and body.
"""

channel = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def my_callback(channel):
    time.sleep(120)
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
                server.sendmail(sender_email, receiver_email, message)

try:
    GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=300)
    while 1:
        time.sleep(100)
except KeyboardInterrupt:
    print("Quitting Program")
    GPIO.cleanup()