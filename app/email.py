from threading import Thread

from flask_mail import Mail, Message

mail = Mail(app)


def send_async_email(app, msg):
    # needs the application context to be created artificially
    # contexts are associated with a thread when mail.send() executes
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(
        app.config["IBLOG_MAIL_SUBJECT_PREFIX"] + subject,
        sender=app.config["IBLOG_MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    # moving email sending function to a background thread
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
