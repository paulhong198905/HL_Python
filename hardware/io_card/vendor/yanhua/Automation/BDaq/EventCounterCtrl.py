#!/usr/bin/python
# -*- coding:utf-8 -*-

from ctypes import c_int

from hardware.io_card.vendor.yanhua.Automation.BDaq.CntrCtrlBase import CntrCtrlBase
from hardware.io_card.vendor.yanhua.Automation.BDaq import Scenario, ErrorCode
from hardware.io_card.vendor.yanhua.Automation.BDaq.EcChannel import EcChannel
from hardware.io_card.vendor.yanhua.Automation.BDaq.BDaqApi import TArray, TEventCounterCtrl


class EventCounterCtrl(CntrCtrlBase):
    def __init__(self, devInfo = None, hostName = None):
        super(EventCounterCtrl, self).__init__(Scenario.SceEventCounter, devInfo, hostName)
        self._ec_channels = []
        self._ec_channels.append(EcChannel(None))
        self._ec_channels = []

    @property
    def channels(self):
        if not self._ec_channels:
            count = self.features.channelCountMax
            nativeArr = TEventCounterCtrl.getChannels(self._obj)
            for i in range(count):
                ecChannObj = EcChannel(TArray.getItem(nativeArr, i))
                self._ec_channels.append(ecChannObj)
        return self._ec_channels

    def read(self, count = 1):
        dataArr = (c_int * count)()
        data = []
        ret = ErrorCode.lookup(TEventCounterCtrl.Read(self._obj, count, dataArr))
        for i in range(count):
            data.append(dataArr[i])
        return ret, data
