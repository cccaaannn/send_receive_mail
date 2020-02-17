def send_mail(sender, password, receivers, subject, body, body_html=None, Cc=[], Bcc=[], attachments=[], use_ssl=True, verbose=3, log_file="send_mail.log",smtp_server_incoming="smtp.gmail.com"):
    """
    sender: email address of the sender
    password: senders email password
    receivers: LIST of email addresses of receivers
    subject: subject of the mail
    body: mail body
    body_html (None): html form of the mail body if exists (you still need to pass a text version of the body if client can't parse html version text version will be shown)
    Cc ([]): LIST of emails of the Cc receivers
    Bcc ([]): LIST of emails of the Bcc receivers
    attachments ([]): LIST of attachment paths to include
    use_ssl (True): uses tls if False
    verbose (3): int value between 0-3 (log levels -> 3 info, 2 warning, 1 error, 0 critical) 
    log_file ("send_mail.log"): log file name if None no file will be use
    smtp_server_incoming ("smtp.gmail.com"): smtp server incoming address
    """
    # import libs
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.base import MIMEBase
    import datetime
    import os
    import logging


    # log stuff
    logger = logging.getLogger("send_mail_logger")  

    # .hasHandlers() is not working 
    # print(logger.handlers)
    # print(logger.hasHandlers())
    # if logger exists don't add new handlers
    if(not logger.handlers):
        verbosity = {0:50,1:40,2:30,3:20}
        if(verbosity.get(verbose)):
            logger.setLevel(verbosity.get(verbose))
        else:
            logger.setLevel(20)
        
        # log formatter
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # file handler
        if(log_file):
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    


    # set message stuff
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

    # parse body as plaintext
    plain = MIMEText(body, "plain")
    message.attach(plain)
    
    # parse body_html as html, email client will try to render the last part first
    if(body_html):
        html = MIMEText(body_html, "html")
        message.attach(html)

    # attachments stuff
    if(attachments):
        for attachment in attachments:
            filename = os.path.basename(attachment)
            try:
                with open(attachment, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email 
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header("Content-Disposition","attachment; filename= {0}".format(filename))

                # Add attachment to message and convert message to string
                message.attach(part)

            except (OSError, IOError) as e:
                logger.warning("error can't include attachment {0} for more info see {1}".format(attachment,log_file), exc_info=True)

    # convert message to string
    message = message.as_string()

    # try to send email
    try:
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

        logger.info("The mail has been sent")
    except Exception as e:
        logger.error("error while sending mail", exc_info=True)
   






