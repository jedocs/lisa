#
# -*- coding: utf-8 -*-
"""
================================================================================
Name:        inspector
Purpose:     (CZE-ZCU-FAV-KKY) Liver medical project

Author:      Pavel Volkovinsky (volkovinsky.pavel@gmail.com)

Created:     08.11.2012
Copyright:   (c) Pavel Volkovinsky 2012
================================================================================
"""

import sys
sys.path.append("../src/")
sys.path.append("../extern/")

import logging
logger = logging.getLogger(__name__)

import numpy

import scipy.ndimage
import sys
"""
import scipy.misc
import scipy.io

import unittest
import argparse
"""

import matplotlib.pyplot as matpyplot
import matplotlib
from matplotlib.widgets import Slider, Button#, RadioButtons

"""
================================================================================
inspector
================================================================================
"""
class inspector:
    
    def __init__(self, data, cmap = matplotlib.cm.Greys_r):
        
        print('Spoustim inspektor dat.')
        
        self.data = data
        self.cmap = cmap
        self.axcolor = 'white' # lightgoldenrodyellow
        
        self.fig = matpyplot.figure()
        
        ## Pridani subplotu do okna (do figure)
        self.ax1 = self.fig.add_subplot(111)
        #self.ax2 = self.fig.add_subplot(122)
        
        ## Upraveni subplotu
        self.fig.subplots_adjust(left = 0.1, bottom = 0.3)
        
        ## Nalezeni a pripraveni obrazku k vykresleni
        self.imgShow = numpy.amax(self.data, 2)
        
        ## Vykreslit obrazek
        self.im1 = self.ax1.imshow(self.imgShow, self.cmap)

       ## Zalozeni mist pro slidery
        # ...
        
        ## Vlastni vytvoreni slideru
        # ...
        
        ## Funkce slideru pri zmene jeho hodnoty
        # ...
        
        ## Zalozeni mist pro tlacitka
        self.axbuttreset = self.fig.add_axes([0.80, 0.08, 0.07, 0.03], axisbg = self.axcolor)
        self.axbuttcontinue = self.fig.add_axes([0.88, 0.08, 0.07, 0.03], axisbg = self.axcolor)
        
        ## Zalozeni tlacitek
        self.breset = Button(self.axbuttreset, 'Reset')
        self.bcontinue = Button(self.axbuttcontinue, 'End editing')
        
        ## Funkce tlacitek pri jejich aktivaci
        self.breset.on_clicked(self.button3DReset)
        self.bcontinue.on_clicked(self.button3DContinue)
        
        self.output = self.data
    
    def showPlot(self):
        
        matpyplot.show()
        
        return self.output
        
    def button3DReset(self, event):
        
        self.imgShow = numpy.amax(self.data, 2)
            
        ## Vykreslit obrazek
        self.im1 = self.ax1.imshow(self.imgShow, self.cmap)
        
        ## Prekresleni
        self.fig.canvas.draw()
        
    def button3DContinue(self, event):
        
        matpyplot.clf()
        matpyplot.close()
