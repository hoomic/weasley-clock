import numpy as np
from threading import Thread, Lock

import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory

import time

factory = PiGPIOFactory()


class Servo(gpiozero.Servo):
  def __init__(self, pin, lo=0, hi=np.pi):
    super().__init__(pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
    self.lo = lo; self.hi = hi
    self.lock = Lock()

  def set_value(self, new_value, delay=0.1):
    self.lock.acquire()
    increase = new_value > self.value
    for v in np.arange(self.value, new_value, 1./256 * (1 if increase else -1)):
      self.value = v
      time.sleep(delay)
    self.value = new_value
    self.lock.release()

  def set_value_threaded(self, value, delay=0.1):
    t = Thread(target=self.set_value, args=(value, delay,))
    t.start()