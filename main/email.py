from flask import render_template
from flask_mail import Message
from main import mail, app


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(clinic):
    token = clinic.get_password_reset_token()
    send_email('Foster Finder - Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[clinic.email],
               text_body=render_template('reset_password_email.txt',
                                         clinic=clinic, token=token),
               html_body=render_template('reset_password_email.html',
                                         clinic=clinic, token=token))