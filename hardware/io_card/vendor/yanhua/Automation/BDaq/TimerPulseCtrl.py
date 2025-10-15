#!/usr/bin/python
# -*- coding:utf-8 -*-

from hardware.io_card.vendor.yanhua.Automation.BDaq import Scenario
from hardware.io_card.vendor.yanhua.Automation.BDaq.CntrCtrlBase import CntrCtrlBase
from hardware.io_card.vendor.yanhua.Automation.BDaq.TmrChannel import TmrChannel
from hardware.io_card.vendor.yanhua.Automation.BDaq.BDaqApi import TArray, TTimerPulseCtrl


class TimerPulseCtrl(CntrCtrlBase):
    def __init__(self, devInfo = None, hostName = None):
        super(TimerPulseCtrl, self).__init__(Scenario.SceTimerPulse, devInfo, hostName)
        self._tmr_channels = []
        self._tmr_channels.append(TmrChannel(None))
        self._tmr_channels = []

    @property
    def channels(self):
        if not self._tmr_channels:
            count = self.features.channelCountMax
            nativeArr = TTimerPulseCtrl.getChannels(self._obj)

            for i in range(count):
                tmrChannObj = TmrChannel(TArray.getItem(nativeArr, i))
                self._tmr_channels.append(tmrChannObj)
        return self._tmr_channels
