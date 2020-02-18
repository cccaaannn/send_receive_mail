def send_mail(sender, password, receivers, subject=None, body=None, body_html=None, Cc=[], Bcc=[], attachments=[], make_receivers_visible=True, use_ssl=True, verbose=3, log_file="send_mail.log",smtp_server_incoming="smtp.gmail.com"):
    """
    sender: email address of the sender
    password: senders email password
    receivers: LIST of email addresses of receivers or str if only one receiver
    subject (None): subject of the mail
    body (None): mail body
    body_html (None): html form of the mail body if exists (you still need to pass a text version of the body if client can't parse html version text version will be shown)
    Cc ([]): LIST of emails of the Cc receivers
    Bcc ([]): LIST of emails of the Bcc receivers
    attachments ([]): LIST of attachment paths to include
    make_receivers_visible (True): if this is False receivers won't shown in thr To part of the mail
    use_ssl (True): uses tls if False
    verbose (3): int value between 0-3 (log levels -> 3 info, 2 warning, 1 error, 0 critical) 
    log_file ("send_mail.log"): log file name if None no file will be use
    smtp_server_incoming ("smtp.gmail.com"): smtp server incoming address

    # returns
    1 on success
    0 on fail
    """
    # import libs
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.base import MIMEBase
    import datetime
    import os

    # log stuff
    logger = __set_logger("send_mail_logger", log_file, verbose)

    # if there is only one sender string is accepted convert it to list
    if(isinstance(receivers, str)):
        receivers = [receivers]

    # set message stuff
    message = MIMEMultipart("alternative")
    message["From"] = sender

    # add subject
    if(subject):
        message["Subject"] = subject

    # add To part
    if(make_receivers_visible):
        for receiver in receivers:
            message["To"] = receiver

    # add cc to the message bcc are hidden 
    if(Cc):
        for c in Cc:
            message["Cc"] = c

    # add Cc and Bcc to receivers list
    receivers = receivers + Cc + Bcc

    # parse body as plaintext
    if(body):
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
        return 1
    except Exception as e:
        logger.error("error while sending mail", exc_info=True)
        return 0


def receive_mail(username, password, include_raw_body = False, attachments_save_path="attachments", mail_box="inbox", mail_count=1, latest_first=True, verbose=3, log_file="receive_mail.log", server_outgoing="imap.gmail.com"):
    import imaplib
    import email
    import os

    # log stuff
    logger = __set_logger("receive_mail_logger", log_file, verbose)


    if(attachments_save_path):
        if(not os.path.exists(attachments_save_path)):
            os.makedirs(attachments_save_path)

    try:
        connection = imaplib.IMAP4_SSL(server_outgoing)
        connection.login(username, password)
    except:
        logger.error("error can't log in to mailbox", exc_info=True)

    try:
        connection.select(mail_box)
        status, mail_datas = connection.search(None, 'ALL')

        if(not status):
            raise Exception("can't search in this mailbox")
    except:
        logger.error("mailbox is not exists", exc_info=True)


    mail_ids = []
    for mail_data in mail_datas:
        mail_ids += mail_data.split()

    # set order
    mail_count = len(mail_ids) # when we reverse it it becomes iterator, we cant get len so I get it here
    if(latest_first):
        mail_ids = reversed(mail_ids)


    mail_counter = 0
    mails = []
    for index, mail_id in enumerate(mail_ids):
        mail_counter += 1
        if(mail_count != -1):
            if(mail_counter > mail_count):
                break
        # the fetch function fetch the email given its id
        # and format that you want the message to be
        status, data = connection.fetch(mail_id, '(RFC822)')

        # the content data at the '(RFC822)' format comes on
        # a list with a tuple with header, content, and the closing
        # byte b')'
        # for response_part in data:
        #     # so if its a tuple...
        #     if isinstance(response_part, tuple):
                # we go for the content at its second element
                # skipping the header at the first and the closing
                # at the third
        message = email.message_from_bytes(data[0][1])

        # with the content we can extract the info about
        # who sent the message and its subject

        # then for the text we have a little more work to do
        # because it can be in plain text or multipart
        # if its not plain text we need to separate the message
        # from its annexes to get the text
        mail_body_text = ""
        mail_body_html = ""
        attachment_names = []
        if message.is_multipart():
            # on multipart we have the text message and
            # another things like annex, and html version
            # of the message, in that case we loop through
            # the email payload
            for part in message.get_payload():
                
                # extract html
                if part.get_content_type() == "text/html":
                    mail_body_html += part.get_payload()

                # extract plaintext
                if part.get_content_type() == "text/plain":
                    mail_body_text += part.get_payload()
                
                # extract attachment
                filename = part.get_filename()
                if(filename):
                    attachment_names.append(filename)
                    # save file if path is given
                    if(attachments_save_path):
                        file_path = os.path.join(attachments_save_path, filename)

                        # change name if file exists
                        file_path = __create_unique_path(file_path)

                        with open(file_path, 'wb') as file:
                            file.write(part.get_payload(decode=True))

                # logger.info("this mail is multipart and contains {0}".format(part.get_content_type()))
                
        else:
            # if the message isn't multipart, just extract it
            mail_body_text = message.get_payload()
        
        logger.info("{0}/{1} id:{2} mail received".format(mail_count, index+1,mail_id))

        if(include_raw_body):
            message_temp = message
        else:
            message_temp = ""

        mail = Mail(message["From"], 
                    message["To"], 
                    message["Cc"], 
                    message["Bcc"], 
                    message["Date"], 
                    message["Subject"],  
                    mail_body_text,
                    mail_body_html,
                    attachment_names,
                    message_temp)

        mails.append(mail)

    return mails


def delete_all_inbox(username, password, mail_box="inbox", delete_batch_size=100, verbose=3, log_file="delete_mail.log", server_outgoing="imap.gmail.com"):
    """
    username: email username
    password: email password
    mail_box ("inbox"): mailbox to delete
    verbose (3): int value between 0-3 (log levels -> 3 info, 2 warning, 1 error, 0 critical) 
    log_file ("delete_mail.log"): log file name if None no file will be use
    server_outgoing ("imap.gmail.com"): imap server outgoing address
    """

    import imaplib

    # log stuff
    logger = __set_logger("delete_mail_logger", log_file, verbose)
    

    try:
        mail = imaplib.IMAP4_SSL(server_outgoing)
        mail.login(username, password)
    except:
        logger.error("error can't log in to mailbox", exc_info=True)

    try:
        mail.select(mail_box)
        status, search_data = mail.search(None, 'ALL')

        if(not status):
            raise Exception("can't search in this mailbox")
    except:
        logger.error("mailbox is not exists", exc_info=True)


    mail_ids = []
    for block in search_data:
        mail_ids += block.split()

    # try to delete
    try:
        last_part = 0
        for i in range(0,len(mail_ids),delete_batch_size):
            if(len(mail_ids) < i+delete_batch_size):
                break
            mail.store("{0}:{1}".format(mail_ids[i].decode(),mail_ids[i+delete_batch_size].decode()), '+FLAGS', '\\Deleted')
            logger.info("mails deleted {0} -> {1}".format(mail_ids[i],mail_ids[i+delete_batch_size]))
            last_part = i

        mail.store("{0}:{1}".format(mail_ids[last_part].decode(),mail_ids[-1].decode()), '+FLAGS', '\\Deleted')
        logger.info("mails deleted {0} -> {1}".format(mail_ids[last_part],mail_ids[-1]))

        # delete mails permanently
        mail.expunge()

    except:
        logger.error("deleteing failed", exc_info=True)

    finally:
        mail.close()
        mail.logout()




class Mail():
    def __init__(self, From, To, Cc, Bcc, Date, subject, body, body_html, attachment_names, body_raw):
        self.From = From
        self.To = To
        self.Cc = Cc
        self.Bcc = Bcc
        self.Date = Date
        self.subject = subject
        self.body = body
        self.body_html = body_html
        self.attachment_names = attachment_names
        self.body_raw = body_raw

    def __str__(self):
        s = ("From: {0}, \nTo: {1}, \nCc: {2}, \nBcc: {3}, \nDate: {4}, \nsubject: {5} \nbody: {6}\n".format(self.From, self.To, self.Cc, self.Bcc, self.Date, self.subject, self.body))
        for index, attachment_name in enumerate(self.attachment_names):
            s += ("attachment {0}: {1}".format(index, attachment_name))
        return s + "\n"


def __create_unique_path(file_path):
    import os
    temp_file_path = file_path
    file_name_counter = 1
    if(os.path.isfile(temp_file_path)):
        while(True):
            save_path, temp_file_name = os.path.split(temp_file_path)
            temp_file_name, temp_file_extension = os.path.splitext(temp_file_name)
            temp_file_name = "{0}-{1}{2}".format(temp_file_name,file_name_counter,temp_file_extension)
            temp_file_path = os.path.join(save_path, temp_file_name)
            file_name_counter += 1
            if(os.path.isfile(temp_file_path)):
                temp_file_path = file_path
            else:
                file_path = temp_file_path
                break

    return file_path


def __set_logger(logger_name, log_file, verbose):
    import logging

    # log stuff
    logger = logging.getLogger(logger_name)  

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

    return logger


