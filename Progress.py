# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progress.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Progress(object):
    def setupUi(self, Progress):
        Progress.setObjectName("Progress")
        Progress.resize(199, 63)
        self.progressBar = QtWidgets.QProgressBar(Progress)
        self.progressBar.setGeometry(QtCore.QRect(10, 30, 171, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(Progress)
        self.label.setGeometry(QtCore.QRect(17, 0, 141, 20))
        self.label.setObjectName("label")

        self.retranslateUi(Progress)
        QtCore.QMetaObject.connectSlotsByName(Progress)

    def retranslateUi(self, Progress):
        _translate = QtCore.QCoreApplication.translate
        Progress.setWindowTitle(_translate("Progress", "Dialog"))
        self.label.setText(_translate("Progress", "Processing PDF  ..."))
