import os
import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from time import sleep
import logging

EMAIL = "weasleyclock.zs@gmail.com"
PASSWORD = os.environ['GMAIL_APP_PASSWORD']
SERVER = "imap.gmail.com"

logger = logging.getLogger("weasley_clock.email_manager")

def send_email(receiver_address, subject):
  try:
    message = MIMEMultipart()
    message['From'] = EMAIL
    message['To'] = receiver_address
    message['Subject'] = subject

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(EMAIL, PASSWORD)

    text = message.as_string()
    session.sendmail(EMAIL, receiver_address, text)
    session.quit()
    logger.info("Sent email to {} with subject {}".format(receiver_address, subject))
  except Exception as e:
    logger.warning("Exception occurred trying to send email: {}".format(e))

class EmailReader():
  def __init__(self):
    self.logged_in = False
    self.login()

  def login(self):
    while not self.logged_in:
      try:
        self.mail = imaplib.IMAP4_SSL(SERVER)
        status, _ = self.mail.login(EMAIL, PASSWORD)
        self.logged_in = status == "OK"
        assert self.logged_in, "login failed"
        logger.info("Successfully logged into email!")
      except Exception as e:
        self.logged_in = False
        logger.warning("Exception occurred trying to login: {}".format(e))
        sleep(10)

  def logout(self):
    self.mail.logout()
    self.logged_in = False

  def read_email(self):
    #login() will only attempt a login when we are logged out
    self.login()
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
      logger.warning("Exception occurred reading email: {}".format(e))
      self.logout()
      return []
