import os
import numpy as np
import requests 

import RPi.GPIO as GPIO

import dropbox

from servo import Servo

#GPIO pins used for the long hand and the short hand
LONG_HAND_PIN = 11
SHORT_HAND_PIN = 12

DB_PATH = '/weasley_clock'
DB_FILE = 'location.txt'

print("Connecting to Dropbox...")
dbx = dropbox.Dropbox(os.environ['DBX_ACCESS_TOKEN'])

# list of locations in clockwise order with where first element corresponds to a 0 angle
locations = ['home', 'work', 'school', 'lost', 'tavern', 'parents', 'mortal peril', 'gym', 'travel', 'bed']

class WeasleyClock():
  def __init__(self):
    self.hands = dict()
    self.hands['Zach'] = Servo(SHORT_HAND_PIN)
    self.hands['Penny'] = Servo(LONG_HAND_PIN)
    self.run()

  def run(self):
    while True:
      # Check to see if a location change has been triggered
      search_result = dbx.files_search(DB_PATH, DB_FILE, max_results=1)
      if len(search_result.matches):
        # if a location change was triggered, download the data and look at the last location
        _, result = dbx.files_download(path=DB_PATH + '/' + DB_FILE)
        command = result.text.split()[-1]
        # process this location
        self.process_command(command)
        # delete the file once it has been processed
        dbx.files_delete(DB_PATH + '/' + DB_FILE)

      self.update()

  def process_command(self, command):
    (person, loc) = command.split(',')
    index = locations.index(loc.lower())
    angle = np.pi * index / len(locations)
    self.hands[person].set_angle(angle)

  def update(self):
    pass


if __name__ == '__main__':
  weasley_clock = WeasleyClock()
  