from flask import current_app, render_template
from flask_mail import Message
from app import mail
import threading

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    if current_app.config['MAIL_SERVER']:
        thr = threading.Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
        thr.start()
    else:
        print(f"Email would be sent: {subject} to {recipients}")

def send_contact_email(data):
    send_email(
        subject=f"Contact Form: {data['subject']}",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config['MAIL_USERNAME']],
        text_body=f"From: {data['name']} <{data['email']}>\n\n{data['message']}",
        html_body=f"<p><strong>From:</strong> {data['name']} &lt;{data['email']}&gt;</p><p>{data['message']}</p>"
    )

def send_pickup_confirmation_email(user, pickup):
    send_email(
        subject="Pickup Scheduled - ReStitch",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=f"Hi {user.name},\n\nYour pickup has been scheduled for {pickup.preferred_slot}.\n\nThank you for choosing ReStitch!",
        html_body=f"<p>Hi {user.name},</p><p>Your pickup has been scheduled for {pickup.preferred_slot}.</p><p>Thank you for choosing ReStitch!</p>"
    )