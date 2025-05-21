import datatransform
import processdiocm
import os
from PyQt5 import QtWidgets
def go (self):
    processdiocm.dicomcrop(self)
    if processdiocm.dicomcrop(self):
        processdiocm.resample_itk(self, 2)
