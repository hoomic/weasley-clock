import os
import numpy as np
import requests 
from time import sleep
from datetime import datetime, timedelta
import logging

import RPi.GPIO as GPIO

from servo import Servo

#GPIO pins used for the long hand and the short hand
LONG_HAND_PIN = 17
SHORT_HAND_PIN = 18

# list of locations in clockwise order with where first element corresponds to a 0 angle
locations = ['home', 'work', 'school', 'walk', 'lost', 'tavern', 'parents', 'mortal peril', 'gym', 'travel', 'bed']

logger = logging.getLogger('weasley_clock')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("weasley_clock.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

#This import has to come after the logger is set up
from email_manager import EmailReader, send_email
email_reader = EmailReader()

# Find the trusted email file
trusted_email_file = None
for root, dirs, files in os.walk(os.path.expanduser('~')):
  for f in files:
    if f == 'weasley_clock_trusted_emails.txt':
      trusted_email_file = root + '/' + f
      trusted_emails = open(trusted_email_file).read().split()
if trusted_email_file is None:
  logger.warning("Could not find weasley_clock_trusted_emails.txt, so allowing commands from ALL emails")
else:
  logger.info("Found trusted email file with entries:\n{}".format('\n'.join(trusted_emails)))

def add_trusted_email(email):
  trusted_emails.append(email)
  with open(trusted_email_file, 'a') as outfile:
    outfile.write('\n{}'.format(email))
  send_email(email, "Congratulations! You can now send commands to WeasleyClock!")

# use this to add emails to weasley_clock_trusted_emails.txt
trusted_email_password = os.environ['TRUSTED_EMAIL_PASSWORD']

class Location():
  def __init__(self, loc, timestamp):
    self.loc = loc
    self.timestamp = timestamp

class WeasleyClock():
  """
  A class for Weasley Clock logic

  ...

  Attributes
  ----------
  hands : dict(str, Servo) 
      a mapping from a person to their corresponding servo
  last_loc : dict(str, Location)
      a mapping from a person to their last location
  trusted_emails : list(str)
      a list of emails that the clock will receive commands from

  Methods
  -------
  run()
      The main loop checking for commands to be sent to the servos
  process_command(person, loc)
      Calculates the servo position and sends the command to the servo
  update()
      Runs periodically for any logic that isn't commanded from the email server         
  """
  def __init__(self):
    self.hands = dict()
    self.hands['zach'] = Servo(SHORT_HAND_PIN)
    self.hands['penny'] = Servo(LONG_HAND_PIN)
    self.last_loc = dict()
    self.run()

  def run(self):
    """
    The main loop checking for commands to be sent to the servos

    Check for emails that follow the person,location,[entered/exited] pattern
    and send those commands to the servos
    """
    while True:
      # Check to see if a location change has been triggered
      for msg in email_reader.read_email():
        try:
          sender = msg['from']
          sender = sender[sender.find('<')+1:-1]
          logger.info("Processing email with subject: {} from: {}".format(msg['subject'], sender))
          if sender not in trusted_emails or trusted_email_file is None:
            # if the subject of the message is the password, then add this email to the trusted email list
            if msg['subject'] == trusted_email_password:
              logger.info("Received email from unkown address with correct password... Adding to list")
              add_trusted_email(sender)
            continue

          
          subject_fields = msg['subject'].split(',')
          exited = False
          if len(subject_fields) == 2:
            person, loc = subject_fields
          elif len(subject_fields) == 3:
            person, loc, exited = msg['subject'].split(',')
            exited = exited.lower().strip() == 'exited'
          person = person.lower().strip()
          loc = loc.lower().strip()
          # if an area is exited, then that person is traveling 
          if exited:
            loc = 'travel'
          if person in self.hands and loc in locations:
            self.process_command(person, loc)
        except Exception as e:
          logger.warning("Exception occured in WeasleyClock.run(): {}".format(e))
          continue
      self.update()
      sleep(10)

  def process_command(self, person, loc):
    """
    Calculates the servo position and sends the command to the servo
    """
    logger.info("Processing Command: {},{}".format(person, loc))
    index = locations.index(loc.lower())
    value= 2 * index / len(locations) - 1
    self.hands[person].set_value_threaded(value)
    self.last_loc[person] = Location(loc, datetime.now())

  def update(self):
    """
    Runs periodically for any logic that isn't commanded from the email server

    if the last location of a person is 'travel', and they have been in that state
    for more than 4 hours, then consider them 'lost'
    """
    now = datetime.now()
    for person, loc in self.last_loc.items():
      if loc.loc == 'travel' and (now - loc.timestamp) > timedelta(hours=4):
        logger.info("{} has been traveling for more than 4 hours... they are lost".format(person))
        self.process_command(person, 'lost')

if __name__ == '__main__':
  weasley_clock = WeasleyClock()
  
