import getpass
from mail_functions import send_mail, receive_mail, delete_all_inbox

sender = "can.kurt.automail@gmail.com"
receivers = ["can.kurt.aa@gmail.com"]
Cc = ["can.kurt.bb@gmail.com"]
attachments=["test_file.txt"]

# password = getpass.getpass()


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

sender = "formatciadam@gmail.com"
password = "12345678Aa*"

# a = []
# for i in range(95):
#     a.append(i)

# last_part = 0
# for i in range(0,len(a),10):
#     print(i)
#     last_part = i

# print(i)



# delete_all_inbox(sender, password, delete_batch_size=5)

# receive_mail2(sender, password)

mail = receive_mail(sender, password, mail_count=2, log_file="logs\\receive_mail.log")

print(mail[0])
print(mail[1])


# send_mail(sender, password, receivers, mail_subject, body, body_html=body_html, Cc=Cc, attachments=attachments)

# for i in range(12):
#     send_mail(sender, password, [sender], "bisey deniyorum{0}".format(i), "bisey deniyorum",body_html=body_html,  attachments=attachments)




