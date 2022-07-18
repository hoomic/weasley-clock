import os
import imaplib
import email

EMAIL = "weasleyclock.zs@gmail.com"
PASSWORD = os.environ['GMAIL_APP_PASSWORD']
SERVER = "imap.gmail.com"

class EmailReader():
  def __init__(self):
    self.login()

  def login(self):
    self.mail = imaplib.IMAP4_SSL(SERVER)
    self.mail.login(EMAIL, PASSWORD)
    print("Successfully logged into email!")

  def logout(self):
    self.mail.logout()

  def read_email(self):
    try:
      status, n_emails = self.mail.select('inbox')
      n_emails = int(n_emails[0])
      # if there are no emails, return empty list
      if n_emails == 0:
        return []

      #loop through emails
      for i in range(n_emails):
        # read the email
        data = self.mail.fetch(str(i+1), '(RFC822)')[1][0][1]
        # parse the data
        msg = email.message_from_string(str(data, 'utf-8'))
        #yield the message
        yield msg
        # delete the message
        self.mail.store(str(i+1), "+FLAGS", "\\Deleted")
    except Exception as e:
      print(e)
      self.logout()
      self.login()
      return []
