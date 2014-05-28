#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Histology analyser GUI
"""

import logging
logger = logging.getLogger(__name__)

import sys
import os.path
path_to_script = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path_to_script, "../extern/dicom2fem/src"))

from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qt import QString

import numpy as np

import datareader
from seed_editor_qt import QTSeedEditor
import py3DSeedEditor

import histology_analyser as HA

class HistologyAnalyserWindow(QMainWindow): 
    HEIGHT = 600
    WIDTH = 800
    
    def __init__(self,inputfile=None,threshold=None,skeleton=False,crop=None,crgui=False):
        self.args_inputfile=inputfile
        self.args_threshold=threshold
        self.args_skeleton=skeleton
        self.args_crop=crop
        self.args_crgui=crgui
        
        QMainWindow.__init__(self)   
        self.initUI()
        
        self.loadData()
        
    def initUI(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.ui_gridLayout = QGridLayout()
        self.ui_gridLayout.setSpacing(15)

        #self.ui_gridLayout.setColumnMinimumWidth(1, 500)
        
        # status bar
        self.statusBar().showMessage('Ready')

        rstart = 0
        
        ### embeddedAppWindow
        self.ui_embeddedAppWindow = MessageDialog('Default window')  
        self.ui_embeddedAppWindow_pos = rstart + 1
        self.ui_gridLayout.addWidget(self.ui_embeddedAppWindow, rstart + 1, 1, 1, 2)
        rstart +=2

        cw.setLayout(self.ui_gridLayout)
        self.setWindowTitle('LISA - Histology Analyser')
        self.show()
    
    def closeEvent(self, event):
        """
        Runs when user tryes to close main window.
        sys.exit(0) - to fix wierd bug, where process is not terminated.
        """
        sys.exit(0)
    
    def processDataGUI(self, data3d=None, metadata=None):
        """
        GUI version of histology analysation algorithm
        """
        self.data3d = data3d
        self.metadata = metadata
        
        ### when input is just skeleton !!! NEEDS TO BE EDITED
        if self.args_skeleton:  #!!!!! NOT TESTED!!!!
            logger.info("input is skeleton")
            struct = misc.obj_from_file(filename='tmp0.pkl', filetype='pickle')
            self.data3d_skel = struct['skel']
            self.data3d_thr = struct['thr']
            self.data3d = struct['data3d']
            self.metadata = struct['metadata']
            self.ha = HA.HistologyAnalyser(self.data3d, self.metadata, self.args_threshold, nogui=False)
            logger.info("end of is skeleton")
            self.fixWindow() # just to be sure
        else:
            ### Generating data if no input file
            if (self.data3d is None) or (self.metadata is None):
                logger.info('Generating sample data...')
                self.setStatusBarText('Generating sample data...')
                self.metadata = {'voxelsize_mm': [1, 1, 1]}
                self.data3d = HA.generate_sample_data(2)
                
            ### Crop data
            self.setStatusBarText('Crop Data')
            if (self.args_crop is None) and (self.args_crgui is True):
                self.data3d = self.cropData(self.data3d)
            elif self.args_crop is not None:    
                crop = self.args_crop
                logger.debug('Croping data: %s', str(crop))
                self.data3d = self.data3d[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
            
            ### Init HistologyAnalyser object
            logger.debug('Init HistologyAnalyser object')
            self.ha = HA.HistologyAnalyser(self.data3d, self.metadata, self.args_threshold, nogui=False)
            
            ### Remove Area
            logger.debug('Remove area')
            self.setStatusBarText('Remove area')
            self.removeArea(self.ha.data3d)

            ### Segmentation
            logger.debug('Segmentation')
            self.setStatusBarText('Segmentation')
            self.showMessage('Segmentation\n1. Select segmentation Area\n2. Select finer segmentation settings\n3. Wait until segmentation is finished')
            
            self.data3d_thr, self.data3d_skel = self.ha.data_to_skeleton()
            self.fixWindow()
        
        ### Show Segmented Data
        logger.debug('Preview of segmented data')
        self.showMessage('Preview of segmented data')
        self.setStatusBarText('Ready')
        self.ha.showSegmentedData(self.data3d_thr, self.data3d_skel)
        self.fixWindow()
        
        ### Computing statistics
        logger.info("######### statistics")
        self.setStatusBarText('Computing Statistics')
        self.showMessage('Computing Statistics\nPlease wait... (it can take very long)')
        
        self.ha.skeleton_to_statistics(self.data3d_thr, self.data3d_skel)
        self.fixWindow()
        
        ### Saving files
        logger.info("##### write to file")
        self.setStatusBarText('Statistics - write file')
        self.showMessage('Writing files\nPlease wait...') ### TO DO!! - file save dialog
        
        self.ha.writeStatsToCSV()
        self.ha.writeStatsToYAML()
        self.ha.writeSkeletonToPickle('skel.pkl')
        #struct = {'skel': self.data3d_skel, 'thr': self.data3d_thr, 'data3d': self.data3d, 'metadata':self.metadata}
        #misc.obj_to_file(struct, filename='tmp0.pkl', filetype='pickle')
        
        ### End
        self.showMessage('Finished')
        self.setStatusBarText('Finished')
        
    def setStatusBarText(self,text=""):
        """
        Changes status bar text
        """
        self.statusBar().showMessage(text)
        QtCore.QCoreApplication.processEvents()
        
    def embedWidget(self, widget=None):     
        """
        Replaces widget embedded that is in gui
        """
        # removes old widget
        self.ui_gridLayout.removeWidget(self.ui_embeddedAppWindow)
        self.ui_embeddedAppWindow.close()
        
        # init new widget
        if widget is None:
            self.ui_embeddedAppWindow = MessageDialog()
        else:
            self.ui_embeddedAppWindow = widget
        
        # add new widget to layout and update
        self.ui_gridLayout.addWidget(self.ui_embeddedAppWindow, self.ui_embeddedAppWindow_pos, 1, 1, 2)
        self.ui_gridLayout.update()
        
        self.fixWindow()
    
    def fixWindow(self,w=None,h=None):
        """
        Resets Main window size, and makes sure all events (gui changes) were processed
        """
        if (w is not None) and (h is not None):
            self.resize(w, h)
        else:    
            self.resize(self.WIDTH, self.HEIGHT)
        QtCore.QCoreApplication.processEvents() # this is very important
    
    def showMessage(self, text="Default"):
        newapp = MessageDialog(text)
        self.embedWidget(newapp)
        
    def removeArea(self, data3d=None):
        if data3d is None:
            data3d=self.ha.data3d
            
        newapp = QTSeedEditor(data3d, mode='mask')
        self.embedWidget(newapp)
        self.ui_embeddedAppWindow.status_bar.hide()
        
        newapp.exec_()
        
        self.fixWindow()
        
    def cropData(self,data3d=None):
        if data3d is None:
            data3d=self.data3d
            
        newapp = QTSeedEditor(data3d, mode='crop')
        self.embedWidget(newapp)
        self.ui_embeddedAppWindow.status_bar.hide()
        
        newapp.exec_()
        
        self.fixWindow()
        
        return newapp.img
        
    def loadData(self):
        newapp = LoadDialog(mainWindow=self, inputfile=self.args_inputfile)
        self.embedWidget(newapp)
        self.fixWindow(self.WIDTH,300)
        newapp.exec_()
        
class MessageDialog(QDialog):
    def __init__(self,text=None):
        self.text = text
        
        QDialog.__init__(self)
        self.initUI()
    
    def initUI(self):
        vbox_app = QVBoxLayout()
        
        font_info = QFont()
        font_info.setBold(True)
        font_info.setPixelSize(20)
        info = QLabel(str(self.text))
        info.setFont(font_info)
        
        vbox_app.addWidget(info)
        vbox_app.addStretch(1) # misto ktery se muze natahovat
        #####vbox_app.addWidget(...) nejakej dalsi objekt
        
        self.setLayout(vbox_app)
        self.show()
        
class LoadDialog(QDialog):
    def __init__(self, mainWindow=None, inputfile=None):
        self.mainWindow = mainWindow
        self.inputfile = inputfile
        
        QDialog.__init__(self)
        self.initUI()
        
        self.importDataWithGui()
    
    def initUI(self):
        self.ui_gridLayout = QGridLayout()
        self.ui_gridLayout.setSpacing(15)

        #self.ui_gridLayout.setColumnMinimumWidth(1, 500)

        rstart = 0
        
        ### Title
        font_label = QFont()
        font_label.setBold(True)        
        ha_title = QLabel('Histology analyser')
        ha_title.setFont(font_label)
        ha_title.setAlignment(Qt.AlignCenter)
        
        self.ui_gridLayout.addWidget(ha_title, rstart + 0, 1)
        rstart +=1
        
        ### Load files buttons etc.
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        font_info = QFont()
        font_info.setBold(True)   
        info = QLabel('Load Data:')
        info.setFont(font_info)
        
        btn_dcmdir = QPushButton("Load DICOM", self)
        btn_dcmdir.clicked.connect(self.loadDataDir)
        btn_datafile = QPushButton("Load file", self)
        btn_datafile.clicked.connect(self.loadDataFile)
        btn_dataclear = QPushButton("Clear data", self)
        btn_dataclear.clicked.connect(self.loadDataClear)
        
        self.text_dcm_dir = QLabel('Data path: ')
        self.text_dcm_data = QLabel('Data info: ')
        
        btn_process = QPushButton("OK", self)
        btn_process.clicked.connect(self.finished)
        
        self.ui_gridLayout.addWidget(hr, rstart + 0, 0, 1, 3)
        self.ui_gridLayout.addWidget(info, rstart + 1, 0, 1, 3)
        self.ui_gridLayout.addWidget(btn_dcmdir, rstart + 2, 0)
        self.ui_gridLayout.addWidget(btn_datafile, rstart + 2, 1)
        self.ui_gridLayout.addWidget(btn_dataclear, rstart + 2, 2)
        self.ui_gridLayout.addWidget(self.text_dcm_dir, rstart + 3, 0, 1, 3)
        self.ui_gridLayout.addWidget(self.text_dcm_data, rstart + 4, 0, 1, 3)
        self.ui_gridLayout.addWidget(btn_process, rstart + 5, 1,)
        rstart +=6
        
        ### Stretcher
        self.ui_gridLayout.addItem(QSpacerItem(0,0), rstart + 0, 0,)
        self.ui_gridLayout.setRowStretch(rstart + 0, 1)
        rstart +=1
        
        ### Setup layout
        self.setLayout(self.ui_gridLayout)
        self.show()
    
    def finished(self,event):
        self.mainWindow.processDataGUI(self.data3d, self.metadata)
    
    def loadDataDir(self,event):
        self.mainWindow.setStatusBarText('Reading DICOM directory...')
        self.inputfile = self.__get_datadir(
            app=True,
            directory=''
        )
        if self.inputfile is None:
            self.mainWindow.setStatusBarText('No DICOM directory specified!')
            return
        self.importDataWithGui()
    
    def loadDataFile(self,event):
        self.mainWindow.setStatusBarText('Reading data file...')
        self.inputfile = self.__get_datafile(
            app=True,
            directory=''
        )
        if self.inputfile is None:
            self.mainWindow.setStatusBarText('No data path specified!')
            return
        self.importDataWithGui()
    
    def loadDataClear(self,event):
        self.inputfile=None
        self.importDataWithGui()
        self.mainWindow.setStatusBarText('Ready')
        
    def __get_datafile(self, app=False, directory=''):
        """
        Draw a dialog for directory selection.
        """

        from PyQt4.QtGui import QFileDialog
        if app:
            dcmdir = QFileDialog.getOpenFileName(
                caption='Select Data File',
                directory=directory
                #options=QFileDialog.ShowDirsOnly,
            )
        else:
            app = QApplication(sys.argv)
            dcmdir = QFileDialog.getOpenFileName(
                caption='Select DICOM Folder',
                #options=QFileDialog.ShowDirsOnly,
                directory=directory
            )
            #app.exec_()
            app.exit(0)
        if len(dcmdir) > 0:

            dcmdir = "%s" % (dcmdir)
            dcmdir = dcmdir.encode("utf8")
        else:
            dcmdir = None
        return dcmdir
        
    def __get_datadir(self, app=False, directory=''):
        """
        Draw a dialog for directory selection.
        """

        from PyQt4.QtGui import QFileDialog
        if app:
            dcmdir = QFileDialog.getExistingDirectory(
                caption='Select DICOM Folder',
                options=QFileDialog.ShowDirsOnly,
                directory=directory
            )
        else:
            app = QApplication(sys.argv)
            dcmdir = QFileDialog.getExistingDirectory(
                caption='Select DICOM Folder',
                options=QFileDialog.ShowDirsOnly,
                directory=directory
            )
            #app.exec_()
            app.exit(0)
        if len(dcmdir) > 0:

            dcmdir = "%s" % (dcmdir)
            dcmdir = dcmdir.encode("utf8")
        else:
            dcmdir = None
        return dcmdir
        
    def importDataWithGui(self):
        if self.inputfile is None:
            self.text_dcm_dir.setText('Data path: '+'Generated sample data')
            self.text_dcm_data.setText('Data info: '+'200x200x200, [1.0,1.0,1.0]')
        else:
            try:
                reader = datareader.DataReader()
                self.data3d, self.metadata = reader.Get3DData(self.inputfile)
            except Exception:
                self.mainWindow.setStatusBarText('Bad file/folder!!!')
                return
            
            voxelsize = self.metadata['voxelsize_mm']
            shape = self.data3d.shape
            self.text_dcm_dir.setText('Data path: '+str(self.inputfile))
            self.text_dcm_data.setText('Data info: '+str(shape[0])+'x'+str(shape[1])+'x'+str(shape[2])+', '+str(voxelsize))
            
            self.mainWindow.setStatusBarText('Ready')
        
if __name__ == "__main__":
    HA.main()
