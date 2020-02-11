import getpass
from mail_functions import send_mail

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

send_mail(sender, password, receivers, mail_subject, body, body_html=body_html, Cc=Cc, attachments=attachments)

