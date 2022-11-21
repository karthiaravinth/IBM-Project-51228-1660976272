import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

def send_email():
    from_email = Email('messigireesh621@gmail.com')
    to_email = To('aravinthkarthi5@gmail.com')
    subject = 'SendGrid mail Checking'
    content = Content("text/plain", "Sendgrid mail content helps to mail other")
    mail = Mail(from_email, to_email, subject, content)
    try:
        sg = SendGridAPIClient('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')
        re = sg.send(mail)
        return re
    except Exception as e:
        return e
        
print(send_email())
