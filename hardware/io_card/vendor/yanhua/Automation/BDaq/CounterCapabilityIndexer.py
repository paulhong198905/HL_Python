#!/usr/bin/python
# -*- coding:utf-8 -*-

from hardware.io_card.vendor.yanhua.Automation.BDaq.CounterIndexer import CounterIndexer
from hardware.io_card.vendor.yanhua.Automation.BDaq import CounterCapability
from hardware.io_card.vendor.yanhua.Automation.BDaq import Utils


class CounterCapabilityIndexer(CounterIndexer):
    def __init__(self, nativeIndexer):
        super(CounterCapabilityIndexer, self).__init__(nativeIndexer, CounterCapability, Utils.toCounterCapability)
