# -*- coding:utf-8 -*-

'''
 MIT License

 Copyright (C) <2019> <@DFRobot Frank>

　Permission is hereby granted, free of charge, to any person obtaining a copy of this
　software and associated documentation files (the "Software"), to deal in the Software
　without restriction, including without limitation the rights to use, copy, modify,
　merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
　permit persons to whom the Software is furnished to do so.

　The above copyright notice and this permission notice shall be included in ALL copies or
　substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
 FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import time

class DFRobot_Expansion_Board:

  _PWM_CHAN_COUNT = 4
  _ADC_CHAN_COUNT = 4

  _REG_SLAVE_ADDR = 0x00
  _REG_PID = 0x01
  _REG_VID = 0x02
  _REG_PWM_CONTROL = 0x03
  _REG_PWM_FREQ = 0x04
  _REG_PWM_DUTY1 = 0x06
  _REG_PWM_DUTY2 = 0x08
  _REG_PWM_DUTY3 = 0x0a
  _REG_PWM_DUTY4 = 0x0c
  _REG_ADC_CTRL = 0x0e
  _REG_ADC_VAL1 = 0x0f
  _REG_ADC_VAL2 = 0x11
  _REG_ADC_VAL3 = 0x13
  _REG_ADC_VAL4 = 0x15

  _REG_DEF_PID = 0xdf
  _REG_DEF_VID = 0x01

  ''' Board status '''
  STA_OK = 0x00
  STA_ERR = 0x01
  STA_ERR_DEVICE_NOT_DETECTED = 0x02
  STA_ERR_SOFT_VERSION = 0x03
  STA_ERR_PARAMETER = 0x04

  ''' last operate status, users can use this variable to determine the result of a function call. '''
  last_operate_status = STA_OK

  ''' Global variables '''
  ALL = 0xffffffff
  
  def _write_bytes(self, reg, buf):
    pass
  
  def _read_bytes(self, reg, len):
    pass

  def __init__(self, addr):
    self._addr = addr

  def begin(self):
    '''
      @brief    Board begin
      @return   Board status
    '''
    pid = self._read_bytes(self._REG_PID, 1)
    vid = self._read_bytes(self._REG_VID, 1)
    if self.last_operate_status == self.STA_OK:
      if pid[0] != self._REG_DEF_PID:
        self.last_operate_status = self.STA_ERR_DEVICE_NOT_DETECTED
      elif vid[0] != self._REG_DEF_VID:
        self.last_operate_status = self.STA_ERR_SOFT_VERSION
      else:
        self.set_pwm_disable()
        self.set_adc_disable()
    return self.last_operate_status

  def set_addr(self, addr):
    '''
      @brief    Set board controler address, reboot module to make it effective
      @param address: int    Address to set, range in 1 to 127
    '''
    if addr < 1 or addr > 127:
      self.last_operate_status = self.STA_ERR_PARAMETER
      return
    self._write_bytes(self._REG_SLAVE_ADDR, [addr])

  def _parse_id(self, limit, id):
    if id == self.ALL:
      return range(1, limit + 1)
    for i in id:
      if i < 1 or i > limit:
        self.last_operate_status = self.STA_ERR_PARAMETER
        return []
    return id

  def set_pwm_enable(self):
    '''
      @brief    Set pwm enable
    '''
    self._write_bytes(self._REG_PWM_CONTROL, [0x01])

  def set_pwm_disable(self):
    '''
      @brief    Set pwm disable
    '''
    self._write_bytes(self._REG_PWM_CONTROL, [0x00])

  def set_pwm_frequency(self, freq):
    '''
      @brief    Set pwm frequency
      @param freq: int    Frequenct to set, in range 1 - 1000
    '''
    if freq < 1 or freq > 1000:
      self.last_operate_status = self.STA_ERR_PARAMETER
      return
    self._write_bytes(self._REG_PWM_FREQ, [freq >> 8, freq & 0xff])

  def set_pwm_duty(self, chan, duty):
    '''
      @brief    Set selected channel duty
      @param chan: list     One or more channels to set, items in range 1 to 4, or chan = self.ALL
      @param duty: float    Duty to set, in range 0.0 to 99.0
    '''
    if duty < 0 or duty > 99:
      self.last_operate_status = self.STA_ERR_PARAMETER
      return
    for i in self._parse_id(self._PWM_CHAN_COUNT, chan):
      self._write_bytes(self._REG_PWM_DUTY1 + (i - 1) * 2, [int(duty), int((duty * 10) % 10)])
  
  def set_adc_enable(self):
    '''
      @brief    Set adc enable
    '''
    self._write_bytes(self._REG_ADC_CTRL, [0x01])

  def set_adc_disable(self):
    '''
      @brief    Set adc disable
    '''
    self._write_bytes(self._REG_ADC_CTRL, [0x00])

  def get_adc_value(self, chan):
    '''
      @brief    Get adc value
      @param chan: int    Channel to get, in range 1 to 4, or self.ALL
      @return :list       List of value
    '''
    l = []
    for i in self._parse_id(self._ADC_CHAN_COUNT, chan):
      rslt = self._read_bytes(self._REG_ADC_VAL1 + (i - 1) * 2, 2)
      l.append((rslt[0] << 8) | rslt[1])
    return l

  def detecte(self):
    '''
      @brief    If you forget address you had set, use this to detecte them, must have class instance
      @return   Board list conformed
    '''
    l = []
    back = self._addr
    for i in range(1, 127):
      self._addr = i
      if self.begin() == self.STA_OK:
        l.append(i)
    for i in range(0, len(l)):
      l[i] = hex(l[i])
    self._addr = back
    self.last_operate_status = self.STA_OK
    return l

import smbus

class DFRobot_Expansion_Board_IIC(DFRobot_Expansion_Board):

  def __init__(self, bus_id, addr):
    '''
      @param bus_id: int   Which bus to operate
      @oaram addr: int     Board controler address
    '''
    self._bus = smbus.SMBus(bus_id)
    DFRobot_Expansion_Board.__init__(self, addr)

  def _write_bytes(self, reg, buf):
    self.last_operate_status = self.STA_ERR_DEVICE_NOT_DETECTED
    try:
      self._bus.write_i2c_block_data(self._addr, reg, buf)
      self.last_operate_status = self.STA_OK
    except:
      pass

  def _read_bytes(self, reg, len):
    self.last_operate_status = self.STA_ERR_DEVICE_NOT_DETECTED
    try:
      rslt = self._bus.read_i2c_block_data(self._addr, reg, len)
      self.last_operate_status = self.STA_OK
      return rslt
    except:
      return [0] * len
