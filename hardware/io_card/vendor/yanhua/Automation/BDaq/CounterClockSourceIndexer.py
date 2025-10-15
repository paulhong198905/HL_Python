#!/usr/bin/python
# -*- coding:utf-8 -*-

from hardware.io_card.vendor.yanhua.Automation.BDaq.CounterIndexer import CounterIndexer
from hardware.io_card.vendor.yanhua.Automation.BDaq import SignalDrop
from hardware.io_card.vendor.yanhua.Automation.BDaq import Utils


class CounterClockSourceIndexer(CounterIndexer):
    def __init__(self, nativeIndexer):
        super(CounterClockSourceIndexer, self).__init__(nativeIndexer, SignalDrop, Utils.toSignalDrop)
