# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from videotrans.configure import config
from videotrans.util import tools


class Ui_parakeetform(object):
    def setupUi(self, parakeet):
        self.has_done = False
        parakeet.setObjectName("parakeet")
        parakeet.setWindowModality(QtCore.Qt.NonModal)
        parakeet.resize(500, 223)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(parakeet.sizePolicy().hasHeightForWidth())
        parakeet.setSizePolicy(sizePolicy)
        parakeet.setMaximumSize(QtCore.QSize(500, 300))


        self.verticalLayout = QtWidgets.QVBoxLayout(parakeet)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.formLayout_2.setFormAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(parakeet)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(100, 35))
        self.label.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")

        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.parakeet_address = QtWidgets.QLineEdit(parakeet)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parakeet_address.sizePolicy().hasHeightForWidth())
        self.parakeet_address.setSizePolicy(sizePolicy)
        self.parakeet_address.setMinimumSize(QtCore.QSize(400, 35))
        self.parakeet_address.setObjectName("parakeet_address")

        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.parakeet_address)
        self.verticalLayout.addLayout(self.formLayout_2)


        self.set_btn = QtWidgets.QPushButton(parakeet)
        self.set_btn.setMinimumSize(QtCore.QSize(0, 35))
        self.set_btn.setObjectName("set_btn")

        self.test = QtWidgets.QPushButton(parakeet)
        self.test.setMinimumSize(QtCore.QSize(0, 30))
        self.test.setObjectName("test")
        help_btn = QtWidgets.QPushButton()
        help_btn.setMinimumSize(QtCore.QSize(0, 35))
        help_btn.setStyleSheet("background-color: rgba(255, 255, 255,0)")
        help_btn.setObjectName("help_btn")
        help_btn.setCursor(Qt.PointingHandCursor)
        help_btn.setText("查看教程" if config.defaulelang == 'zh' else "The tutorial")
        help_btn.clicked.connect(lambda: tools.open_url(url='https://pyvideotrans.com/parakeet'))

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.setObjectName("layout_btn")

        self.layout_btn.addWidget(self.set_btn)
        self.layout_btn.addWidget(self.test)
        self.layout_btn.addWidget(help_btn)

        self.verticalLayout.addLayout(self.layout_btn)



        self.retranslateUi(parakeet)
        QtCore.QMetaObject.connectSlotsByName(parakeet)

    def retranslateUi(self, parakeet):
        parakeet.setWindowTitle("parakeet-tdt api")
        self.label.setText("http地址" if config.defaulelang == 'zh' else 'parakeet url')
        self.parakeet_address.setPlaceholderText(
            '填写 github.com/jianchang512/parakeet-api 项目启动后的http地址' if config.defaulelang == 'zh' else 'Fill in the HTTP address after the "github.com/jianchang512/parakeet-api" program starts')
        self.set_btn.setText('保存' if config.defaulelang == 'zh' else "Save")
        self.test.setText('测试' if config.defaulelang == 'zh' else "Test")
