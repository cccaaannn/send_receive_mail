import getpass
from mail_functions import send_mail, receive_mail, delete_all_inbox

sender = "can.kurt.automail@gmail.com"
receivers = ["can.kurt.aa@gmail.com"]
Cc = ["can.kurt.bb@gmail.com"]
attachments=["test_file.txt"]

password = getpass.getpass()


mail_subject = "test mail"

body = """\
Hi,
How are you?
"""
body_html = """\
<html>
<body>
<p>Hi,<br>
How are you?<br>
<a href="https://www.google.com/">this is a link</a> 
</p>
</body>
</html>
"""



for i in range(12):
    send_mail(sender, password, sender, subject="test {0}".format(i), body=body, body_html=body_html, attachments=attachments, log_file="logs\\receive_mail.log")


mails = receive_mail(sender, password, mail_count=-1, log_file="logs\\receive_mail.log")

print(mails[0])
print(mails[1])


# delete_all_inbox(sender, password, delete_batch_size=50)

# send_mail(sender, password, receivers, mail_subject, body, body_html=body_html, Cc=Cc, attachments=attachments)





