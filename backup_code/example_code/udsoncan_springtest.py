'''
Notice:
修改ReadDataByIdetifier.py 代码：
#payload_size = len(codec)    #wkm updated on 2022/12/05 --注释掉原代码此行，重新赋值payload_size = len(response.data)- offset

修改pcan.py 文件的_recv_internal()函数，注释如下两行
 else:
    # raise PcanCanOperationError(self._get_formatted_error(result))
'''


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread,pyqtSignal
from airspring_filling import Ui_airspring
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
from udsoncan.exceptions import *
import udsoncan.configs
import isotp
import can
import ics
import time
import GlobalB_DID_Codec
import os
import json
from can.bit_timing import BitTimingFd,BitTiming

from can.interfaces.pcan.pcan import PcanBus


def parse_DTC(payload_data):  #解析DTC。返回类型为 list [DTC code1,DTC code2,....],若No DTC,反馈空数组[]
   '''
   Positive reponse message definition - reportDTCbyStatusMask $02
   byte 1: ReadDTCInformation Response Service ID - $59
   byte 2: reportType = [ reportDTCbyStatusMask] - $02
   byte 3: DTCStatusAvailabilityMask
   byte 4: DTCHighByte#1
   byte 5: DTCLowByte#1
   byte 6: DTCFailureTypeByte#1
   byte 7: statusOfDTC#1
   byte 8: DTCHighByte#2
   byte 9: DTCLowByte#2
   byte 10: DTCFailureTypeByte#2
   byte 11: statusOfDTC#2
   :return：type is list
   '''
   DTCcount = int((len(payload_data)-2)/4)
   print('parse_DTC function print->DTC qty: %s' % DTCcount)
   DTC_codes = []
   if DTCcount ==0:
       print('no DTC')
       return DTC_codes
   else:
       for i in range(DTCcount): #转换故障码格式为P/U/B等格式
          code1 = ''.join( [ "%02X" % x for x in payload_data[i*4+2:i*4+6] ] ).strip()   #hex to string
          if code1[0] == '0':
             codehead = 'P0'
          elif code1[0] == '1':
             codehead = 'P1'
          elif code1[0] == '2':
             codehead = 'P1'
          elif code1[0] == '3':
             codehead = 'P3'
          elif code1[0] == '4':
             codehead = 'C0'
          elif code1[0] == '5':
             codehead = 'C1'
          elif code1[0] == '5':
             codehead = 'C2'
          elif code1[0] == '7':
             codehead = 'C3'
          elif code1[0] == '8':
             codehead = 'B0'
          elif code1[0] == '9':
             codehead = 'B1'
          elif code1[0] == 'A':
             codehead = 'B2'
          elif code1[0] == 'B':
             codehead = 'B3'
          elif code1[0] == 'C':
             codehead = 'U0'
          elif code1[0] == 'D':
             codehead = 'U1'
          elif code1[0] == 'E':
             codehead = 'U2'
          elif code1[0] == 'F':
             codehead = 'U3'

          code1 = codehead + code1[1:]
          DTC_codes.append(code1)

   return get_DTC_explain(DTC_codes)

def get_DTC_explain(DTC_codes): #获取DTC的解析信息，输入参数为DTC code（带status信息）
    '''
    :param DTC_codes: DTC list
    :return: explain DTC and status, type is list. [[DTC code1, english meaning, status1,status2,...],[DTC code2, english meaning, status1,status2,...],...]
    '''
    DTC_list = []
    try:
        DTCdatabasepath = os.getcwd() + '\database\GM_DTC_Json.json'   #DTCdatabase（GM_DTC_Json.json）文件放在DTCdatabase文件夹下
        with open(DTCdatabasepath, encoding='utf-8') as f:
            jsondict = json.loads(json.load(f))

    except:
        jsondict={}

    if len(DTC_codes) >0:
        for DTC_code in DTC_codes:
            single_DTCcode_exp = []  # [DTC code,DTC english meaning, status1, status2,....]
            DTC = DTC_code[:-2]
            status_code = int(DTC_code[-2:],16)  #DTC status byte

            if DTC in jsondict:  #get DTC english description, if json has DTC description,get it, if not, give an unknown DTC for description
                DTC_explain = jsondict[DTC]
            else:
                DTC_explain = 'unknown DTC'

            single_DTCcode_exp.append(DTC_code[:-2])
            single_DTCcode_exp.append(DTC_explain)
            if status_code & 0x01:
                single_DTCcode_exp.append('Test Failed')
            if status_code & 0x02:
                single_DTCcode_exp.append('test_failed_this_operation_cycle')
            if status_code & 0x04:
                single_DTCcode_exp.append('pending')
            if status_code & 0x08:
                single_DTCcode_exp.append('confirmed')
            if status_code & 0x10:
                single_DTCcode_exp.append('test_not_completed_since_last_clear')
            if status_code & 0x20:
                single_DTCcode_exp.append('test_failed_since_last_clear')
            if status_code & 0x40:
                single_DTCcode_exp.append('test_not_completed_this_operation_cycle')
            if status_code & 0x80:
                single_DTCcode_exp.append('warning_indicator_requested')
            DTC_list.append(single_DTCcode_exp)
        print(single_DTCcode_exp)

    return DTC_list



config = dict(udsoncan.configs.default_client_config)
config['p2_timeout'] = 5
config['standard_version'] = 2006     #2006之后的版本，发送10诊断服务后，会更改P2-timeout时间
config['data_identifiers'] = {
   0xF190: udsoncan.AsciiCodec(17),                # Codec that read ASCII string. We must tell the length of the string
   0xF1A0: GlobalB_DID_Codec.hex_to_int_Codec,     # hex(udsoncan.DidCodec),MEC
   0xF1CB: GlobalB_DID_Codec.hex_to_int_Codec,     # GMEndModelPartNumber
   0xF1DB: udsoncan.AsciiCodec(2),                 # GMEndModelPartNumberAlphaCode
   0xF180: GlobalB_DID_Codec.F18x_Codec,           # BootSoftwareIdentificationDataIdentifier
   0xF181: GlobalB_DID_Codec.F18x_Codec,           # AppSoftwareIdentificationDataIdentifier
   0xF182: GlobalB_DID_Codec.F18x_Codec,           # AppDataIdentificationDataIdentifier
   0xF1CC: GlobalB_DID_Codec.hex_to_int_Codec,     # GMBaseModelPartNumber
   0xF1DC: udsoncan.AsciiCodec(2),                 # GMEndModelPartNumberAlphaCode
   0xF0F3: GlobalB_DID_Codec.hex_to_string_Codec,  # ECUID
   0xF0F6: GlobalB_DID_Codec.F0F6_Codec,           # BootInfoBlockSubjectNameandECUName
   0xF0F4: GlobalB_DID_Codec.hex_to_string_Codec,  # SignatureBypassAuthorizationTicket
   0xF080: GlobalB_DID_Codec.hex_to_int_Codec,     # ECUKeyProvisionStateFlag
   0xF081: GlobalB_DID_Codec.hex_to_string_Codec,  # ECUKeyConfigurationData
   0xF0B4: udsoncan.AsciiCodec(16),                # ManufacturingTraceabilityCharacters
   0xF199: GlobalB_DID_Codec.hex_to_string_Codec,  # ProgrammingDate
   0x5134:GlobalB_DID_Codec.bytesCodec,

}

isotp_params = {
      'stmin': 0, #7/2从0修改为32  # Will request the sender to wait 32ms between consecutive frame. 0-127ms or 100-900ns with values from 0xF1-0xF9
      'blocksize': 0,  # Request the sender to send 8 consecutives frames before sending a new flow control message.# 流控帧单包大小,0为不限制
      'wftmax': 0,  # Number of wait frame allowed before triggering an error
      'tx_data_length': 8,  # Link layer (CAN layer) works with 8 byte payload (CAN 2.0)
      'tx_data_min_length': None,   # Minimum length of CAN messages. When different from None, messages are padded to meet this length. Works with CAN 2.0 and CAN FD.
      'tx_padding': 0,  # Will pad all transmitted CAN messages with byte 0x00.
      'rx_flowcontrol_timeout': 1000,  # Triggers a timeout if a flow control is awaited for more than 1000 milliseconds
      'rx_consecutive_frame_timeout': 1000,   # Triggers a timeout if a consecutive frame is awaited for more than 1000 milliseconds
      # 'squash_stmin_requirement': False,   # When sending, respect the stmin requirement of the receiver. If set to True, go as fast as possible.
      'max_frame_size': 4095,  # Limit the size of receive frame.
      'can_fd': True,
      # 'bitrate_switch':True
   }
timingFD = BitTimingFd(f_clock=80_000_000, nom_brp=10, nom_tseg1=12, nom_tseg2=3, nom_sjw=1, data_brp=4, data_tseg1=7, data_tseg2=2, data_sjw=1)
# timingFD = BitTimingFd(f_clock=40000000, nom_brp=5, nom_tseg1=11, nom_tseg2=4, nom_sjw=1, data_brp=4, data_tseg1=3, data_tseg2=1, data_sjw=1)


#子线程：发送3E 80
class Example(QThread):
    signal = pyqtSignal(str)

    def __init__(self,bus):
        super(Example,self).__init__()
        self.bus = bus

    def run(self):
         while start_3E_status==True:

             try:
                # bus = can.interface.Bus(bustype='neovi', channel=ics.NETID_HSCAN, bandrate=200000)
                data = [0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00]
                msg = can.Message(is_extended_id=True,arbitration_id=0x14DA58F1, data=data, is_rx=False)  #
                self.bus.send(msg)
                print('Tx:[0x3E,0x80]')
                self.signal.emit('Tx:[0x3E,0x80]')
                time.sleep(2)
             except:
                 self.signal.emit('error, pls check connection and try again!')
                 return




class Ui_Dialog(Ui_airspring):
    def __init__(self,Dialog):
        super().setupUi(Dialog) #调用父类的setupUi函数
        # self.bustype = 'neovi'  # bus type设置
        # self.channel = ics.NETID_HSCAN  #channel setting
        # self.bustype = 'pcan'
        # self.channel = 'PCAN_USBBUS1'
        self.bitrate = 200000 #200000   #bitrate setting
        self.txid = 0x14DA28F1  #0x14DA7DF1'
        self.rxid = 0x14DAF128

        # UDSonCAN
        # self.udsoncan_functionaddress = 0x10DBFEF1  # uds on can function logical address
        # self.bus = can.interface.Bus(bustype=self.bustype, channel=self.channel, bandrate=self.bitrate)
        # self.conn = self.create_conn()
        # self.th = Example(self.bus)   #实例化多进程对象，处理3E周期发送
        self.pushButton_startfill.clicked.connect(self.start_filling)  #开始加注
        # self.th.signal.connect(self.onUpdateText)  # 多进程信号槽连接


    def onUpdateText(self, text):
        self.textBrowser_datadisplay.append(text)  # 在指定的区域显示提示信息
        self.textBrowser_datadisplay.moveCursor(self.textBrowser_datadisplay.textCursor().End)  # 文本框显示到底部
        QtWidgets.QApplication.processEvents()  # 一定加上这个功能，不然有卡顿

    def check_device_connection(self):
        # ************  在bus前，防止程序报错，加上find device   *****************
        devices = ics.find_devices()  # find intrepidCS device



        if len(devices) == 0:
            print('do not find device,pls check if connected with device')
            return False
        else:
            return True

    def start_filling(self):
        global start_3E_status  # create a global var to stop / start 3E tester present
        # self.check_device_connection()
        #检查设备是否已连接
        # if self.check_device_connection() == False:
        #     self.onUpdateText('do not find device,pls check if connected with device')
        #     return

        self.onUpdateText('开始加注')
        if self.send_wakeupmsg():
            start_3E_status = False
        else:
            start_3E_status = False

        print('创建timing or timingFD')
        # timing = BitTiming(f_clock=8_000_000, brp=4, tseg1=7, tseg2=1, sjw=1)
        timingFD = BitTimingFd(f_clock=80000000, nom_brp=10, nom_tseg1=12, nom_tseg2=3, nom_sjw=1, data_brp=4,
                               data_tseg1=7, data_tseg2=2, data_sjw=1)
        # bus = PcanBus(channel='PCAN_USBBUS1',bitrate=500000,timing=timingFD) #

        # bus = can.interface.Bus(bustype=self.bustype, channel=self.channel, bandrate=self.bitrate, fd=True)
        # if start_3E_status:
        #     # bus_3E = can.interface.Bus(bustype=self.bustype, channel=self.channel, bandrate=self.bitrate)
        #     self.th = Example(bus=bus)
        #     self.th.signal.connect(self.onUpdateText)  # 多进程信号槽连接
        #     # self.th.start()  # 启动线程
        #     pass

        #监听can数据
        # bus = can.interface.Bus(bustype=self.bustype, channel=self.channel, bandrate=self.bitrate)
        # bus = PcanBus(channel='PCAN_USBBUS1', bitrate=500000, timing=timingFD)
        # reader = can.BufferedReader()
        # notifier = can.Notifier(bus, [reader])
        # bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000,timing=timingFD,fd=True)
        print('建立bus')
        bus = PcanBus(channel='PCAN_USBBUS1', bitrate=500000, timing=timingFD)
        tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=self.txid,rxid=self.rxid)  # Network layer addressing scheme
        # tp_addr = isotp.Address(isotp.AddressingMode.Extended_29bits, txid=self.txid,rxid=self.rxid)  # Network layer addressing scheme

        if start_3E_status:
            self.th = Example(bus=bus)
            self.th.signal.connect(self.onUpdateText)  # 多进程信号槽连接
            self.th.start()  # 启动线程



        print('定义tp_address')
        stack = isotp.CanStack(bus=bus, address=tp_addr,params=isotp_params)  # Network/Transport layer (IsoTP protocol)
        conn = PythonIsoTpConnection(stack)
        with Client(conn,request_timeout=2, config=config) as client:
            try:
                self.onUpdateText('进入扩展模式')
                print('进入扩展模式')
                response = client.change_session(0x03)  #send 1003
                print(response)
                # print(response.code)  #正反馈时.code == 0
                print('send 1003 response: ',response.positive)  #.positive 判断是否正反馈，正反馈为True
                if response.positive:
                    self.onUpdateText(''.join(["%02X" % x for x in response.data]).strip())
                    self.onUpdateText('1003正反馈')
                    #1003正反馈，session-control图标变绿
                    self.pushButton_sessionctrl_indicator.setStyleSheet("QPushButton {\n"
                                                                        "    border-radius: 30px;\n"
                                                                        "    border-style: outset;\n"
                                                                        "    background: qradialgradient(\n"
                                                                        "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                        "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                        "        );\n"
                                                                        "    padding: 5px;\n"
                                                                        "    background-color: Green;\n"
                                                                        "\n"
                                                                        "    }\n"
                                                                        "\n"
                                                                        "")
                else:
                    self.onUpdateText('1003负反馈')
            except:
                self.pushButton_sessionctrl_indicator.setStyleSheet("QPushButton {\n"
                                                                    "    border-radius: 30px;\n"
                                                                    "    border-style: outset;\n"
                                                                    "    background: qradialgradient(\n"
                                                                    "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                    "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                    "        );\n"
                                                                    "    padding: 5px;\n"
                                                                    "    background-color: red;\n"
                                                                    "\n"
                                                                    "    }\n"
                                                                    "\n"
                                                                    "")
            time.sleep(1)



            try:
                print('Tx: 22 F1 A0 读取MEC值')
                self.onUpdateText('Tx: 22 F1 A0 读取MEC值')
                response = client.read_data_by_identifier(0xF1A0)
                MECvalue = response.service_data.values[0xF1A0]
                print(MECvalue)
                self.onUpdateText('模块MEC值为：{}'.format(MECvalue))
                # print('read %02X' % 0xF1A0, response.service_data.values[0xF1A0])
            except:
                self.onUpdateText('MEC读取失败')
            time.sleep(5)
            #读零件号
            try:
                print('Tx: 22 F1 CB 读取零件号')
                self.onUpdateText('Tx: 22 F1 CB 读取零件号')
                response = client.read_data_by_identifier(0xF1CB)
                print('读取零件号反馈状态： ',response.positive)  # .positive 判断是否正反馈，正反馈为True
                partNumberValue = response.service_data.values[0xF1CB]
                print('读取零件号为：{}'.format(partNumberValue))
                self.onUpdateText('读取零件号为：{}'.format(partNumberValue))
                # print('read %02X' % 0xF1A0, response.service_data.values[0xF1A0])
            except:
                self.onUpdateText('零件号读取失败')
            time.sleep(5)

            # 读故障码
            print('读取模块DTC')
            self.onUpdateText('读取模块DTC')
            try:
                response = client.read_dtc_information(subfunction=0x02,
                                                       status_mask=0xAF)  # subfunction 0x02:reportDTCbyStatusMask
                print('DTC response: ', response.positive)
                self.read_DTC(client)
                self.pushButton_readinfo_indicator.setStyleSheet("QPushButton {\n"
                                                                 "    border-radius: 30px;\n"
                                                                 "    border-style: outset;\n"
                                                                 "    background: qradialgradient(\n"
                                                                 "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                 "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                 "        );\n"
                                                                 "    padding: 5px;\n"
                                                                 "    background-color: Green;\n"
                                                                 "\n"
                                                                 "    }\n"
                                                                 "\n"
                                                                 "")
            except:
                self.onUpdateText('读取模块DTC失败')
                self.pushButton_readinfo_indicator.setStyleSheet("QPushButton {\n"
                                                                 "    border-radius: 30px;\n"
                                                                 "    border-style: outset;\n"
                                                                 "    background: qradialgradient(\n"
                                                                 "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                 "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                 "        );\n"
                                                                 "    padding: 5px;\n"
                                                                 "    background-color: red;\n"
                                                                 "\n"
                                                                 "    }\n"
                                                                 "\n"
                                                                 "")
            time.sleep(5)

            cr_rrprssDID = 0x5134     #Read Corners and Reservior Pressure DID
            fillstatusDID = 0x512C    #read fill status
            #0-Service_still_running
            #1-Service_completed_without_error
            #2-Service_completed_terminated_with_error
            #3-Temperature_too_high
            #4-Vehicle_Speed_Too_High
            #5-Voltage_Too_High
            #6-Voltage_Too_Low
            #7-Error_mode_DTC_active
            #8-Reservoir_pressure_too_low
            #9-Air_spring_pressure_too_high
            #10-Time_out_of_subfunction
            #11-Conditions_Not_Correct
            #读储气罐压力值，DID为xx
            self.read_Corners_ReserviorPrss(client=client,cr_rrprssDID=cr_rrprssDID)

            #储气罐给前空气悬架气囊分气 - 31指令,拿到spec后改为正确的指令
            routine_id = 0x0385
            control_type = 0x01
            data_LFfill = 0x0A0046
            data_LRfill = 0x220046
            data_RFfill = 0x120046
            data_RRfill = 0x420046

            print('完成分气')
            self.onUpdateText('完成分气')

            bus.shutdown()



        start_3E_status = False
        # time.sleep(5)
        # conn.close()
        # notifier.stop()  # 停止监听总线数据
        # while True:
        #     msg = reader.get_message()        #timeout=5
        #     # print('Rx msg_:', msg)
        #     if msg !=None:
        #         if msg.arbitration_id in [self.txid,self.rxid]:
        #             print('Rx msg_:', msg)
        #             # print('arbid:',hex(msg.arbitration_id),':',hex(msg.arbitration_id)[-2:])
        #     if msg is None:
        #         print('msg is null')
        #         break


    def send_wakeupmsg(self):
        '''
        send wake up msg, if send successful,return True, else return false
        :return: bool
        '''
        # ************  在bus前，防止程序报错，加上find device   *****************
        # devices = ics.find_devices()  # find intrepidCS device
        # if len(devices) == 0:
        #     print('do not find device,pls check if connected with InterpidCS device')
        #     self.textBrowser_datadisplay.append(
        #         "<font color = 'red'>" + 'do not find device,pls check if connected with InterpidCS device' + "<font>")
        #     # return False
        # else:
        if True:
            # print(devices[0])
            # bus = can.interface.Bus(bustype=self.bustype, channel=self.channel, bandrate=self.bitrate)
            bus = PcanBus(channel='PCAN_USBBUS1', bitrate=500000)
            wakeupdata = [0x44, 0x50, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00]
            wakeupmsg = can.Message(is_extended_id=False, arbitration_id=0x638, data=wakeupdata)
            # wakeupdata = [0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            # wakeupmsg = can.Message(is_extended_id=False, arbitration_id=0x638, data=wakeupdata)

            self.onUpdateText('Tx: '+ '[0x44, 0x50, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00]')
            try:
                for i in range(3):
                    bus.send(wakeupmsg)  # wake up CAN
                    time.sleep(0.5)
                # msg = bus.recv(timeout=0.5)
                # while len(msg) >0:
                #     print(msg)
                self.onUpdateText('唤醒模块成功')
                self.pushButton_wakeup_indicator.setStyleSheet("QPushButton {\n"
                                                                    "    border-radius: 30px;\n"
                                                                    "    border-style: outset;\n"
                                                                    "    background: qradialgradient(\n"
                                                                    "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                    "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                    "        );\n"
                                                                    "    padding: 5px;\n"
                                                                    "    background-color: Green;\n"
                                                                    "\n"
                                                                    "    }\n"
                                                                    "\n"
                                                                    "")
            except:
                self.onUpdateText('唤醒模块失败')
                self.pushButton_wakeup_indicator.setStyleSheet("QPushButton {\n"
                                                                    "    border-radius: 30px;\n"
                                                                    "    border-style: outset;\n"
                                                                    "    background: qradialgradient(\n"
                                                                    "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                    "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                    "        );\n"
                                                                    "    padding: 5px;\n"
                                                                    "    background-color: red;\n"
                                                                    "\n"
                                                                    "    }\n"
                                                                    "\n"
                                                                    "")
            bus.shutdown()
            print('complete sending wakeup')
            return True

    def read_DTC(self,client):
        ECUDTClist = []
        try:
            response = client.read_dtc_information(subfunction=0x02,
                                                   status_mask=0xAF)  # subfunction 0x02:reportDTCbyStatusMask
            print('DTC response: ',response.positive)
            print('故障码反馈值：',response.data)  # response.data数据 -> byte0：subfunction
            ECUDTCcodes = parse_DTC(response.data)  # 调用parse_DTC函数，解析故障码. 返回list
            print('DTClist:', ECUDTCcodes)
            # self.onUpdateText('{} Positive Response'.format(hex(self.txid)))
            ECUDTClist.append([self.txid, ' Positive Response'])  # add ECU Positive Response information
            if len(ECUDTCcodes) > 0:
                for ECUDTCcode in ECUDTCcodes:
                    self.onUpdateText('{} {}'.format(ECUDTCcode[0], ECUDTCcode[1]))
                    ECUDTClist.append(ECUDTCcode)
            # 读取ECU信息成功后，图标置绿色

        except NegativeResponseException as e:  # handle negative response
            print('Server refused our request for service %s with code "%s" (0x%02x)'
                  % (e.response.service.get_name(), e.response.code_name, e.response.code))
            ECUDTClist.append([self.txid, ' Negative Response'])

        except (InvalidResponseException, UnexpectedResponseException) as e:
            print('Server sent an invalid payload : %s' % e.response.original_payload)
            ECUDTClist.append([self.txid, ' InvalidResponseException or UnexpectedResponseException'])

        except:
            print('{} Response Timeout'.format(self.txid))
            self.onUpdateText('{} Response Timeout'.format(self.txid))
            # raise TimeoutError('ECU no response')
            ECUDTClist.append([self.txid, ' Response Timeout'])

    #读取气弹簧 & 气罐压力值
    def read_Corners_ReserviorPrss(self,client,cr_rrprssDID):
        self.onUpdateText('读储气罐压力值：')
        self.textBrowser_airtankpressure.clear()
        self.textBrowser_LFpressure.clear()
        self.textBrowser_RFpressure.clear()
        self.textBrowser_RRpressure.clear()
        try:
            response = client.read_data_by_identifier(cr_rrprssDID)  # Read Corners and  Reservior Pressure DID:0x5134
            print('打印反馈状态：', response.positive)
            print(response.service_data.values[cr_rrprssDID])
            if response.positive:
                AirSuspensionPressure = response.service_data.values[cr_rrprssDID][3] * 0.1
                LFPressure = response.service_data.values[cr_rrprssDID][2] * 0.1
                LRPressure = response.service_data.values[cr_rrprssDID][4] * 0.1
                RFPressure = response.service_data.values[cr_rrprssDID][5] * 0.1
                RRPressure = response.service_data.values[cr_rrprssDID][6] * 0.1

                self.textBrowser_airtankpressure.append('{} bar'.format(AirSuspensionPressure))
                self.textBrowser_LFpressure.append('{} bar'.format(LFPressure))
                self.textBrowser_RFpressure.append('{} bar'.format(RFPressure))
                self.textBrowser_RRpressure.append('{} bar'.format(RRPressure))
                self.textBrowser_LRpressure.append('{} bar'.format(LRPressure))

                self.onUpdateText('读储气罐压力值：{}'.format(AirSuspensionPressure))
                # print('读储气罐压力值：{}'.format(AirTankPressure))
                self.pushButton_readpressure_indicator.setStyleSheet("QPushButton {\n"
                                                                     "    border-radius: 30px;\n"
                                                                     "    border-style: outset;\n"
                                                                     "    background: qradialgradient(\n"
                                                                     "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                     "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                     "        );\n"
                                                                     "    padding: 5px;\n"
                                                                     "    background-color: Green;\n"
                                                                     "\n"
                                                                     "    }\n"
                                                                     "\n"
                                                                     "")
            else:
                self.textBrowser_airtankpressure.append('未读取到储气罐压力值')
                self.pushButton_readpressure_indicator.setStyleSheet("QPushButton {\n"
                                                                     "    border-radius: 30px;\n"
                                                                     "    border-style: outset;\n"
                                                                     "    background: qradialgradient(\n"
                                                                     "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                     "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                     "        );\n"
                                                                     "    padding: 5px;\n"
                                                                     "    background-color: red;\n"
                                                                     "\n"
                                                                     "    }\n"
                                                                     "\n"
                                                                     "")
        except:
            self.pushButton_readpressure_indicator.setStyleSheet("QPushButton {\n"
                                                                 "    border-radius: 30px;\n"
                                                                 "    border-style: outset;\n"
                                                                 "    background: qradialgradient(\n"
                                                                 "        cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,\n"
                                                                 "        radius: 1.35, stop: 0 #fff, stop: 1 #888\n"
                                                                 "        );\n"
                                                                 "    padding: 5px;\n"
                                                                 "    background-color: red;\n"
                                                                 "\n"
                                                                 "    }\n"
                                                                 "\n"
                                                                 "")
            pass




if __name__ == "__main__":
  import sys
  app = QtWidgets.QApplication(sys.argv)
  Dialog = QtWidgets.QDialog()
  winflags = QtCore.Qt.Dialog
  # 添加最小化按钮
  winflags |= QtCore.Qt.WindowMinimizeButtonHint
  winflags |= QtCore.Qt.WindowMaximizeButtonHint
  # 添加关闭按钮
  winflags |= QtCore.Qt.WindowCloseButtonHint
  Dialog.setWindowFlags(winflags)
  ui = Ui_Dialog(Dialog)
  # ui.setupUi(Dialog)
  Dialog.show()
  sys.exit(app.exec_())
