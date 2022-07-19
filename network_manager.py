import os
import requests
from time import sleep

class Network():
  def __init__(self, ssid, psk, key_mgmt="WPA-PSK"):
    self.ssid = ssid
    self.psk = psk
    self.key_mgmt = key_mgmt

  @classmethod
  def from_file(cls, lines):
    ssid, psk, key_mgmt = None, None, None
    for line in lines:
      try:
        idx = line.find('=')
        if idx == -1:
          continue
        field = line[:idx]
        value = line[idx+1:]
        value = value.strip('"')
        if field == 'ssid':
          ssid = value
        elif field == 'psk':
          psk = value
        elif field == 'key_mgmt':
          key_mgmt = value
      except:
        continue
    if ssid is None or psk is None or key_mgmt is None:
      return
    return cls(ssid, psk, key_mgmt)

  def __eq__(self, other):
    return self.ssid == other.ssid and self.psk == other.psk and self.key_mgmt == other.key_mgmt

  def __str__(self):
    return 'network={{\n\tssid=\"{}\"\n\tpsk=\"{}\"\n\tkey_mgmt={}\n}}\n'.format(self.ssid, self.psk, self.key_mgmt)

  def __hash__(self):
    return hash(self.ssid)

def find_wifi_credentials():
  for root, dirs, files in os.walk('/media/', topdown=False):
    for file in files:
      if file == "wifi_network.txt":
        network_creds = open(root + '/' + file).read().split()
        return Network(*network_creds)

def connected():
  try:
    requests.get("http://www.google.com", timeout=5)
    return True
  except:
    return False

class NetworkManager():
  def __init__(self, wpa_supplicant_file='/etc/wpa_supplicant/wpa_supplicant.conf'):
    self.networks = set()
    self.wpa_supplicant_file = wpa_supplicant_file
    self.read_wifi_credentials()
    self.connect_if_not_connected()

  def read_wifi_credentials(self):
    infile = open(self.wpa_supplicant_file)
    lines = infile.read().split()
    i = 0
    while i < len(lines):
      network_lines = []
      if lines[i].startswith('network'):
        j = 1
        while not lines[i+j].startswith('}'):
          network_lines.append(lines[i + j])
          j += 1
        self.networks.add(Network.from_file(network_lines))
        i += j
      else:
        i += 1

  def connect_if_not_connected(self):
    while True:
      if not connected():
        network = find_wifi_credentials()
        # Only write network and reboot if we aren't connected and we don't already know this network
        if network is not None and network not in self.networks:
          outfile = open(self.wpa_supplicant_file, 'a')
          outfile.write('\n{}'.format(network))
          outfile.close()
          os.system("sudo reboot")
      sleep(60)

if __name__ == '__main__':
  nm = NetworkManager()