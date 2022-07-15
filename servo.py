import numpy as np

import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory

import time

factory = PiGPIOFactory()

class Servo(gpiozero.Servo):
  def __init__(self, pin, lo=0, hi=np.pi):
    super().__init__(pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
    self.lo = lo; self.hi = hi
    self.angle = 0

  def set_angle(self, angle, delay=0.1):
    angle = max(self.lo, min(self.hi, angle))
    new_value = angle / (np.pi/2) - 1.0
    increase = new_value > self.value
    for v in np.arange(self.value, new_value, 1./256 * (1 if increase else -1)):
      self.value = v
      time.sleep(delay)
    self.value = new_value
    self.angle = angle

  def increment_angle(self, increment, delay=0.1):
    delay = max(0.01, delay)
    self.set_angle(self.angle + increment, delay)
