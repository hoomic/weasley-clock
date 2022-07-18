import numpy as np
import requests 
from time import sleep
import logging

import RPi.GPIO as GPIO

from email_reader import EmailReader

from servo import Servo

#GPIO pins used for the long hand and the short hand
LONG_HAND_PIN = 17
SHORT_HAND_PIN = 18

email_reader = EmailReader()

# list of locations in clockwise order with where first element corresponds to a 0 angle
locations = ['home', 'work', 'school', 'lost', 'tavern', 'parents', 'mortal peril', 'gym', 'travel', 'bed']

class WeasleyClock():
  def __init__(self):
    self.hands = dict()
    self.hands['zach'] = Servo(SHORT_HAND_PIN)
    self.hands['penny'] = Servo(LONG_HAND_PIN)
    self.run()

  def run(self):
    while True:
      # Check to see if a location change has been triggered
      for msg in email_reader.read_email():
        try:
          logging.info("Processing email with subject: {}".format(msg['subject']))
          person, loc = msg['subject'].split(',')
          person = person.lower()
          loc = loc.lower()
          if person in self.hands and loc in locations:
            self.process_command(person, loc)
        except Exception as e:
          print(e)
          continue
      self.update()
      sleep(10)

  def process_command(self, person, loc):
    logging.info("Processing Command: {},{}".format(person, loc))
    index = locations.index(loc.lower())
    value= 2 * index / len(locations) - 1
    self.hands[person].set_value_threaded(value)

  def update(self):
    pass

if __name__ == '__main__':
  logging.basicConfig(filename="weasley_clock.log", encoding='utf-8', level=logging.DEBUG)
  weasley_clock = WeasleyClock()
  
