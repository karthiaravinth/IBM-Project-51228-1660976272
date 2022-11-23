import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

def send_email(mail):
    if mail is None:
        to = 'messigireesh621@gmail.com' #default mail
    else:
        to = mail
    from_email = Email('aravinthkarthi5@gmail.com')
    to_email = To(to)
    subject = 'SendGrid mail Checking'
    content = Content("text/plain", "Sendgrid mail content helps to mail other")
    mail = Mail(from_email, to_email, subject, content)
    try:
        sg = SendGridAPIClient('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')
        re = sg.send(mail)
        return True
    except Exception as e:
        return False
       