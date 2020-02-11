
def send_mail(sender, password, receivers, subject, body, body_html=None, Cc=[], Bcc=[], attachments=[], use_ssl=True, show_info=True, smtp_server_incoming="smtp.gmail.com"):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.base import MIMEBase
    import datetime
    import os

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    
    for receiver in receivers:
        message["To"] = receiver

    # add cc to the message
    # bcc are hidden
    if(Cc):
        for c in Cc:
            message["Cc"] = c

    # add Cc and Bcc to receivers list
    receivers = receivers + Cc + Bcc

    # Turn these into plain/html MIMEText objects
    plain = MIMEText(body, "plain")
    message.attach(plain)
    
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    if(body_html):
        html = MIMEText(body_html, "html")
        message.attach(html)


    if(attachments):
        for attachment in attachments:
            filename = os.path.basename(attachment)
            try:
                with open(attachment, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email 
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header("Content-Disposition","attachment; filename= {0}".format(filename))

                # Add attachment to message and convert message to string
                message.attach(part)

            except (OSError, IOError) as e:
                print(e,"attachment error")


    message = message.as_string()

    if(use_ssl):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server_incoming, 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, message)
    else:
        connection = smtplib.SMTP(smtp_server_incoming, 587)
        connection.ehlo()
        connection.starttls()
        connection.ehlo()
        connection.login(sender, password)
        connection.sendmail(sender, receivers, message)
        connection.close()
    
    if(show_info):
        print("The mail has been sent. Time:{0}".format(str(datetime.datetime.now().time())[0:8]))







