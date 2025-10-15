import udsoncan
import struct

class F18x_Codec(udsoncan.DidCodec):   #read boot/AppSW/AppData IdentificationDataIdentifier--F180/F181/F182
   def __init__(self): #type_len:读取DID反馈值的字节长度
      self.type_len = 0    # encoded payload is 4 byte long.

   def decode(self, payload):
      # F18x反馈值的byte1为ECU标定数量,byte2:标定item(如01,02,...)，零件号：byte3~6，DLS：byte7~8 .......
      cals = {}
      # cal_flag = 0   #
      for cal_flag in range(int(payload[0])):
         pn = struct.unpack('>L', payload[cal_flag * 7 + 2 : cal_flag * 7 + 6])[0]
         suffix = (payload[cal_flag * 7 + 6 : cal_flag * 7 + 8]).decode('ascii')
         cals[payload[cal_flag * 7 + 1]] = str(pn) + '.' + suffix
      #print(cals)
      return cals

   def __len__(self): #type_len:读取DID反馈值的字节长度
      return self.type_len    # encoded payload is 4 byte long.

class hex_to_int_Codec(udsoncan.DidCodec):
   def __init__(self): #type_len:读取DID反馈值的字节长度
      self.type_len = 0    # encoded payload is 4 byte long.

   def decode(self, payload):
      print('payload:',payload)
      self.type_len = len(payload)
      if self.type_len == 1:
         structpack_format = '>B'
      elif self.type_len == 4:
         structpack_format = '>L'
      else:
         structpack_format = '>p'
      #print('payload:',payload)
      val = struct.unpack(structpack_format, payload)[0]  # decode the 32 bits value
      return val                        # Do some stuff (reversed)

   def __len__(self): #type_len:读取DID反馈值的字节长度
      return self.type_len    # encoded payload is 4 byte long.

class hex_to_string_Codec(udsoncan.DidCodec):
   def __init__(self,type_len=0): #type_len:读取DID反馈值的字节长度
      self.type_len = type_len    # encoded payload is 4 byte long.

   def decode(self, payload):
      val = ''.join(["%02X" % x for x in payload]).strip()  # hex to string
      return val                        #

   def __len__(self): #type_len:读取DID反馈值的字节长度
      return self.type_len    # encoded payload is 4 byte long.


class F0F6_Codec(udsoncan.DidCodec):  #BootInfoBlockSubjectNameandECUName
   def __init__(self,type_len=0):
      self.type_len = type_len    # encoded payload is 4 byte long.

   def to_ascii(self,h):
      list_s = []
      for i in range(0, len(h)):
         list_s.append(chr(h[i]))
      return ''.join(list_s)

   def decode(self, payload):
      #val = self.to_ascii(payload[15:])  #F0F6 read ECU name,response的第13位开始，为ECU name信息
      #print('F0F6 read payload:',payload)
      val=payload[15:].decode('utf-8').strip(b'\x00'.decode())
      # print('F0F6 read payload:',val)
      return val

   def __len__(self): #
      return self.type_len

class hexCodec(udsoncan.DidCodec):  #将bytes格式 转换为 十六进制字符串
   def __init__(self,type_len=0):
      self.type_len = type_len    # encoded payload


   def decode(self, payload):
      #val = self.to_ascii(payload[15:])  #F0F6 read ECU name,response的第13位开始，为ECU name信息
      #print('F0F6 read payload:',payload)
      # val=payload[15:].decode('utf-8').strip(b'\x00'.decode())
      # print('F0F6 read payload:',val)
      list_s = []
      for i in range(0, len(payload)):
         list_s.append('%02X' % payload[i])
      val = ' '.join(list_s)
      return val

   def __len__(self): #
      return self.type_len


class bytesCodec(udsoncan.DidCodec):  #read DID, return unhandle bytes
   def __init__(self,type_len=0):
      self.type_len = type_len    # encoded payload


   def decode(self, recv_payload)->bytes:
      val=recv_payload
      return val

   def __len__(self): #
      return self.type_len

GMDIDDict = {
   0xF0F3: 'ECUID',
   0xF1CC: 'BMPN',
   0xF1CB: 'EMPN',
   0xF0B4: 'ManufacturingTraceabilityCharacters'
}