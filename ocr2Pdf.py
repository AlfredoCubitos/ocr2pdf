#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
import sys, io, os, subprocess, time
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QListWidgetItem, QGraphicsScene, QGraphicsItem, QMessageBox, QGraphicsPixmapItem, QDialog
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QKeyEvent
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QBuffer, Qt, QRectF, QRect, QUrl, QThreadPool
from PIL import ImageEnhance, Image, ImageQt
from multithread import Worker, WorkerSignals

import numpy as np
#from ui_configform import Ui_Form
from Progress import Ui_Progress

class GraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
    
        self.point1 = [0,0]
        self.point2 = [0,0]
        self.rect = None

    croped = pyqtSignal(list, list)
    wheeled = pyqtSignal(int)
    
    def mouseMoveEvent(self,event):
        print(event.scenePos().x()," : " ,event.scenePos().y())
        self.rect.setRect(QRectF(self.point1[0],self.point1[1], event.scenePos().x(),event.scenePos().y()))
        
    def mousePressEvent(self, event):

        self.point1[0] = event.scenePos().x()
        self.point1[1] = event.scenePos().y()

        if self.rect:
            self.removeItem(self.rect)

        self.rect = self.addRect(QRectF(self.point1[0],self.point1[1],self.point2[0],self.point2[1]),QPen(Qt.black,4,Qt.DotLine))
        #self.rect.setPen(QPen(Qt.black,2,Qt.DotLine))
        
        
        #print(event.scenePos().x())
    
    def mouseReleaseEvent(self, event):
        self.point2[0] = event.scenePos().x()
        self.point2[1] = event.scenePos().y()
        self.update()
        self.croped.emit(self.point1,self.point2)
    
    def wheelEvent(self, event):
        self.wheeled.emit(event.delta())
        print(str(event.delta()))
    
    def removeRect(self):
        self.removeItem(self.rect)

 


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("configform.ui", self)
     
        #self.ui = Ui_Form()
        #self.ui.setupUi(self)
        
        self.dialog = QDialog()

        self.ui.brigthnesSlider.valueChanged.connect(self.brigthnesSlot)
        self.ui.contrastSlider.valueChanged.connect(self.contrastSlot)

        self.ui.brigthnessLcd.valueChanged.connect(self.setBrightSlider)
        self.ui.contrastLcd.valueChanged.connect(self.setContastSlider)

        self.ui.btnOpenFiles.clicked.connect(self.openFiles)
        self.ui.listWidget.itemClicked.connect(self.openImage)
        self.ui.listWidget.currentItemChanged.connect(self.imageItemChanged)
        self.ui.btnLeft.clicked.connect(self.turnLeft)
        self.ui.btnRight.clicked.connect(self.turnRight)
        self.ui.btnSave.clicked.connect(self.saveImage)
        self.ui.btnCrop.clicked.connect(self.saveCroped)
        self.ui.btnSaveTes.clicked.connect(self.saveTesFile)
        self.ui.btnOcrStart.clicked.connect(self.createPdf)

        self.scene = GraphicsScene()
        
        
        self.scene.croped.connect(self.getCropedImage)
        self.scene.wheeled.connect(self.zoom)

        self.threadpool = QThreadPool()
        
        
        self.pixmap = QPixmap()
        self.pixmapItem = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmapItem)
        #self.pixmap.load("Calibrate_Test_1.png")
        self.buffer = QBuffer()
        self.pilBufferImg = "/tmp/san2foldertempimg.png"
        self.tesFile = ""

        self.brightSet=False
        self.contrastSet=False
        self.imChanged=False
        self.imSaved=True
        self.cropP1 = [0,0]
        self.cropP2 = [0,0]

        self.rotate = 0
        self.path = ""

        self.bright = self.ui.brigthnesSlider.maximum()/2
        self.contrast = self.ui.contrastSlider.maximum()/2
        
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Delete:
            items = []
            for i in range(self.ui.listWidget.count()):
                if self.ui.listWidget.item(i).isSelected():
                    items.append(i)
            
            for i in items:
                item = self.ui.listWidget.takeItem(i)
                del item
                

    def openFiles(self):
        fileDlg = QFileDialog(self)
        fileDlg.setNameFilter("Images (*.png *.jpg *.tif *.pmb)")
        fileNames = fileDlg.getOpenFileNames(self,"Select images",".","Images (*.png *.jpg *.tif *.pmb)")
    
        self.ui.listWidget.addItems(fileNames[0])
        if (self.ui.listWidget.count() > 0):
            self.ui.btnSaveTes.setEnabled(True)
    
    @pyqtSlot()
    def turnRight(self):
        rot = 45
        self.ui.view.rotate(rot)
        self.rotate += rot
        if self.rotate > 360:
            self.rotate = 0

        
    @pyqtSlot()
    def turnLeft(self):
        rot = -45
        self.ui.view.rotate(rot)
        self.rotate += rot
        if self.rotate < -360:
            self.rotate = 0

    @pyqtSlot()
    def saveImage(self):
        #rotated = self.im.rotate(self.rotate)
        img = self.scene.items()
        img = img[0].pixmap()
        img.save(self.path)
        self.imSaved = True
        #rotated.save(self.path)
    
    
    @pyqtSlot(QListWidgetItem,QListWidgetItem)
    def imageItemChanged(self,currentItem,prevItem):
        self.openImage(currentItem)

    
    @pyqtSlot(QListWidgetItem)
    def openImage(self, item):
  
        if not self.imSaved:
            self.imgSaveMsgBox()

        self.path = item.text()
        self.im = Image.open(self.path)
        img = ImageQt.ImageQt(self.im.convert('RGBA'))
        #self.imageP = self.scene.addPixmap(self.pixmap.fromImage(img))
        #self.imageP.grabMouse()
        self.pixmapItem.setPixmap(self.pixmap.fromImage(img))
        self.ui.view.setScene(self.scene)
        #self.ui.view.scale(0.15,0.15)
        self.ui.view.fitInView(self.pixmapItem,Qt.KeepAspectRatio)
        self.ui.btnSave.setEnabled(True)
        self.ui.btnRight.setEnabled(True)
        self.ui.btnLeft.setEnabled(True)
        self.ui.brigthnesSlider.setEnabled(True)
        self.ui.contrastSlider.setEnabled(True)
        self.ui.brigthnessLcd.setEnabled(True)
        self.ui.contrastLcd.setEnabled(True)
        self.ui.btnOcrStart.setEnabled(True)
        self.setBufferImage()

        if self.ui.brigthnesSlider.value() != self.bright:
            self.brigthnesSlot(self.ui.brigthnesSlider.value())

        if self.ui.contrastSlider.value() != self.contrast:
            self.contrastSlot(self.ui.contrastSlider.value())


    @pyqtSlot(int)
    def brigthnesSlot(self,int):
        
        val =int/10
        self.ui.brigthnessLcd.blockSignals(False)
        self.ui.brigthnessLcd.setValue(val)
        self.ui.brigthnessLcd.blockSignals(True)
        contrast = self.ui.contrastSlider.value()/10
        self.enhanceImage(val,contrast)

    
    @pyqtSlot(int)
    def contrastSlot(self,int):
        val =int/10
        self.ui.contrastLcd.blockSignals(True)
        self.ui.contrastLcd.setValue(val)
        self.ui.contrastLcd.blockSignals(False)

        bright = self.ui.brigthnesSlider.value()/10
        self.enhanceImage(bright,val)


    @pyqtSlot(float)
    def setBrightSlider(self,val):
        value = val*10
        self.ui.brigthnesSlider.blockSignals(True)
        self.ui.brigthnesSlider.setValue(int(value))
        self.ui.brigthnesSlider.blockSignals(False)
    
    @pyqtSlot(float)
    def setContastSlider(self,val):
        value = val*10
        self.ui.contrastSlider.blockSignals(True)
        self.ui.contrastSlider.setValue(int(value))
        self.ui.contrastSlider.blockSignals(False)

    @pyqtSlot(list,list)
    def getCropedImage(self,p1,p2):
        self.cropP1 = p1
        self.cropP2 = p2
        self.ui.btnCrop.setEnabled(True)
        
        

    @pyqtSlot()
    def saveCroped(self):
        rect = QRect(self.cropP1[0], self.cropP1[1],self.cropP2[0],self.cropP2[1])
        # pix = self.imageP.pixmap().copy(rect)
        pix = self.pixmapItem.pixmap().copy(rect)
        # self.scene.removeItem(self.imageP)
        #self.imageP = self.scene.addPixmap(pix)
        self.pixmapItem.setPixmap(pix)
        #pix.save("/home/manni/croped.png")
        self.ui.btnCrop.setEnabled(False)
        self.scene.removeRect()
        self.imSaved = False
    
    @pyqtSlot(int)
    def zoom(self,z):
        

        if z == 120:
            self.view.scale(1.5, 1.5)
           
        else:
            self.view.scale(1.0/1.5, 1.0/1.5)
            
    @pyqtSlot()
    def saveTesFile(self):
        url = QUrl()
        url.setUrl(self.ui.listWidget.item(0).text())
        #print(self.ui.listWidget.item(0).text())
        startDir = url.adjusted(QUrl.RemoveFilename).toString()
        
        file = QFileDialog.getSaveFileName(self, "Directory to store .tes file", startDir, "Tes file (*.tes)")
        if len(file[0]) < 1:
            return
       # print(file[0])
        self.tesFile = file[0]
        f = open(self.tesFile,'w')
        for i in  range(self.ui.listWidget.count()):
            f.write(self.ui.listWidget.item(i).text()+"\n")
            print(self.ui.listWidget.item(i).text()) 
        f.close()

        self.ui.btnOcrStart.setEnabled(True)
    
    @pyqtSlot()
    def createPdf(self):
        
        if not os.path.exists(self.tesFile):
            msgBox = QMessageBox()
            msgBox.setText("File error")
            msgBox.setInformativeText("no tes file found\n aborting process")
            print("no tes file found aborting process ....")
            msgBox.exec()
            return
        
        self.processPdf()
    
    @pyqtSlot(int)    
    def setProcessValue(self,int):
        self.processDlg.progressBar.setValue(int)

    def processPdf(self):
        self.processDlg = Ui_Progress()
        self.processDlg.setupUi(self.dialog)
        self.dialog.setModal(True)
        self.dialog.show()
       # time.sleep(200)
        self.startThread(self.runTesseract,None,self.thread_complete)
        #self.runTesseract("none")
    
    def runTesseract(self):
        (h , t)= os.path.split(self.tesFile)
        fn = t.split(".")
        #count = self.ui.listWidget.count()
        proc = subprocess.Popen(["tesseract","-l","deu",self.tesFile,fn[0],"pdf"],stdout=subprocess.PIPE)
        ## importantant if communicate is not set subprocess will return immediately
        ## while the tesseract process is still running
        proc.communicate()[0]
        
    def setBufferImage(self):
        img = self.pixmapItem.pixmap()
        self.buffer.open(QBuffer.ReadWrite)
        img.save(self.buffer,"PNG")
        self.pilBufferImg = Image.open(io.BytesIO(self.buffer.data()))
        self.buffer.close()
    
    def imgSaveMsgBox(self):
        msgBox = QMessageBox()
        msgBox.setText("The image has been modified.")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec()

        if ret == QMessageBox.Save:
            self.saveImage()
            return
        if ret == QMessageBox.Cancel:
            self.imSaved = True
            return


    def enhanceImage(self, bright, cont):
       # self.setBufferImage()
        brightness = ImageEnhance.Brightness(self.pilBufferImg)
        pilImg = brightness.enhance(bright)
        contrast = ImageEnhance.Contrast(pilImg)
        pilImg = contrast.enhance(cont)
        self.pixmapItem.setPixmap(self.pixmap.fromImage(ImageQt.ImageQt(pilImg.convert('RGBA'))))  
    
    def startThread(self, fn, resultFn=None, complete=None):
        worker = Worker(fn) # Any other args, kwargs are passed to the run function
        if resultFn is not None:
            worker.signals.result.connect(resultFn)
        if complete is not None:
            worker.signals.finished.connect(complete)
        #worker.signals.progress.connect(setProcessValue)
        self.threadpool.start(worker)
        

    
    def thread_complete(self):
        
        for i in (52,65,78,90,100):
            time.sleep(1)
            self.processDlg.progressBar.setValue(i)
            
        self.dialog.close()
        print("Thread completed")

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow() 
    window.show()
    sys.exit(app.exec_())
