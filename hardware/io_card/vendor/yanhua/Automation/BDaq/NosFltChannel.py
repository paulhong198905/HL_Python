#!/usr/bin/python
# -*- coding:utf-8 -*-

from hardware.io_card.vendor.yanhua.Automation.BDaq.NoiseFilterChannel import NoiseFilterChannel


class NosFltChannel(NoiseFilterChannel):
    def __init__(self, nativeNoiseFilterChannObj):
        super(NosFltChannel, self).__init__(nativeNoiseFilterChannObj)
