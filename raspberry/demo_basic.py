# -*- coding:utf-8 -*-

'''
  # demo_basic.py
  #
  # Connect board with raspberryPi.
  # Run this demo.
  #
  # All pwm channel will set frequency to 1000HZ, duty to 50%, attention: PWM voltage depends on independent power supply
  # All adc channel value will print on terminal
  #
  # Copyright   [DFRobot](http://www.dfrobot.com), 2016
  # Copyright   GNU Lesser General Public License
  #
  # version  V1.0
  # date  2019-3-28
'''

import time

from DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board

board = Board(1, 0x10)    # Select i2c bus 1, set address to 0x10

def board_detect():
  l = board.detecte()
  print("Board list conform:")
  print(l)

''' print last operate status, users can use this variable to determine the result of a function call. '''
def print_board_status():
  if board.last_operate_status == board.STA_OK:
    print("board status: everything ok")
  elif board.last_operate_status == board.STA_ERR:
    print("board status: unexpected error")
  elif board.last_operate_status == board.STA_ERR_DEVICE_NOT_DETECTED:
    print("board status: device not detected")
  elif board.last_operate_status == board.STA_ERR_PARAMETER:
    print("board status: parameter error")
  elif board.last_operate_status == board.STA_ERR_SOFT_VERSION:
    print("board status: unsupport board framware version")

if __name__ == "__main__":

  board_detect()    # If you forget address you had set, use this to detected them, must have class instance

  # Set board controler address, use it carefully, reboot module to make it effective
  '''
  board.set_addr(0x10)
  if board.last_operate_status != board.STA_OK:
    print("set board address faild")
  else:
    print("set board address success")
  '''

  while board.begin() != board.STA_OK:    # Board begin and check board status
    print_board_status()
    print("board begin faild")
    time.sleep(2)
  print("board begin success")

  board.set_pwm_enable()                # Pwm channel need external power
  # board.set_pwm_disable()
  board.set_pwm_frequency(1000)         # set frequency to 1000HZ, Attention: PWM voltage depends on independent power supply
  board.set_pwm_duty(board.ALL, 50.0)   # Set all pwm channels duty
  # board.set_pwm_duty([board.CHANNEL1, board.CHANNEL2], 50.0)    # Use list to set channels duty that selected

  board.set_adc_enable()
  # board.set_adc_disable()

  while True:
    val_list = board.get_adc_value(board.ALL)    # return a list contains adc values
    print("adc values, 0 - 3.3v, 12bits, max = 4096")
    chan = 0
    for val in val_list:
      print("channel: %d, value: %d, valtage: %.2fV" %(chan, val, float(val) / 4096.0 * 3.3))
      chan += 1
    print("")
    time.sleep(2)
