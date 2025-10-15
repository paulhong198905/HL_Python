
from hardware.io_card.vendor.yanhua.Automation.BDaq.CntrCtrlBase import CntrCtrlBase
from hardware.io_card.vendor.yanhua.Automation.BDaq import Scenario
from hardware.io_card.vendor.yanhua.Automation.BDaq.PoChannel import PoChannel
from hardware.io_card.vendor.yanhua.Automation.BDaq.BDaqApi import TArray, TPwModulatorCtrl


class PwModulatorCtrl(CntrCtrlBase):
    def __init__(self, devInfo = None, hostName = None):
        super(PwModulatorCtrl, self).__init__(Scenario.ScePwModulator, devInfo, hostName)
        self._po_channels = []
        self._po_channels.append(PoChannel(None))
        self._po_channels = []

    @property
    def channels(self):
        if not self._po_channels:
            count = self.features.channelCountMax
            nativeArr = TPwModulatorCtrl.getChannels(self._obj)

            for i in range(count):
                poChannObj = PoChannel(TArray.getItem(nativeArr, i))
                self._po_channels.append(poChannObj)
        return self._po_channels
