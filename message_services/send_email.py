from app import mail,app
from flask_mail import Message
from werkzeug.exceptions import BadRequest
from threading import Thread


def send_email(app, msg):
    try:
        with app.app_context():
            mail.send(msg)
    except ConnectionRefusedError:
        raise BadRequest('Connection Refused Error')

def email(recipients,text_body,html_body, subject):
    msg = Message()
    msg.subject = subject
    msg.recipients = recipients
    msg.sender = app.config['MAIL_USERNAME']
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_email, args=(app,msg))
    send_email(app,msg)

