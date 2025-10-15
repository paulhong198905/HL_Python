#!/usr/bin/python
# -*- coding:utf-8 -*-

from hardware.io_card.vendor.yanhua.Automation.BDaq.AnalogInputChannel import AnalogInputChannel


class AiChannel(AnalogInputChannel):
    def __init__(self, nativeChannelObj):
        super(AiChannel, self).__init__(nativeChannelObj)
