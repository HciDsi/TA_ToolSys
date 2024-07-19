import sys

import maya.cmds
from PySide2 import QtWidgets

sys.path.append('D:/Project/DCC_Plug_in/Maya/MeshSelectionTool')

import maya.cmds as cmds
import maya.mel as mel
import pymel

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import MeshSelection


class Selection(object):

    def __init__(self):
        self.gui_name = "MeshSelection"
        self.gui_title = "Metarial Selection Tool"
        self.gui = QWidget()
        self.init_Gui(self.gui)

        self.obj_list = []

    def init_Gui(self, Form):
        if not Form.objectName():
            Form.setObjectName(self.gui_name)
        Form.resize(450, 800)

        Form.setWindowTitle(self.gui_title)

        self.create_menus(Form)
        self.create_layout(Form)

    def create_menus(self, Form):
        self.menu_bar = QtWidgets.QMenuBar(Form)

        self.window_menu = self.menu_bar.addMenu("Window")
        self.clear_menu = QtWidgets.QAction("Clear")
        self.window_menu.addAction(self.clear_menu)

        self.edit_menu = self.menu_bar.addMenu("Edit")

        self.help_menu = self.menu_bar.addMenu("Help")

    def create_layout(self, Form):
        # main_layout
        self.main_layout = QtWidgets.QVBoxLayout(Form)
        self.main_layout.setMenuBar(self.menu_bar)  # 设置菜单栏

        self.head_layout = QtWidgets.QHBoxLayout(Form)

        self.container = QWidget()
        self.object_layout = QtWidgets.QVBoxLayout(self.container)
        self.container.setLayout(self.object_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container)

        self.main_layout.addLayout(self.head_layout)
        self.main_layout.addWidget(self.scroll_area)

        # head_layout
        self.obj_l = QLabel("Object :")

        self.obj_in = QLineEdit()
        self.obj_in.setReadOnly(True)

        self.get_button = QPushButton("<")
        self.get_button.clicked.connect(self.get_object)

        self.head_layout.addWidget(self.obj_l)
        self.head_layout.addWidget(self.obj_in)
        self.head_layout.addWidget(self.get_button)

        # object_layout


    def get_object(self):
        if not self.is_selection_shape():
            return

        self.clear_layout(self.object_layout)
        for n in self.obj_list:
            temp_layout = QtWidgets.QVBoxLayout()
            temp_layout.addWidget(QLabel(n))

            temp_lv = QtWidgets.QVBoxLayout()
            temp_wt = QWidget()
            temp_wt.setLayout(temp_lv)
            temp_sa = QScrollArea()
            temp_sa.setWidget(temp_wt)
            temp_sa.setWidgetResizable(True)
            temp_layout.addWidget(temp_sa)
            for a in range(0, 9):
                temp_lv.addWidget(QPushButton(str(a)))
            temp_lv.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            temp_widget = QWidget()
            temp_widget.setLayout(temp_layout)
            temp_widget.setFixedHeight(300)

            self.object_layout.addWidget(temp_widget)
            self.object_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def is_selection_shape(self):
        # Implement logic to check if the selection is a shape

        selection = cmds.ls(selection=True)
        if not selection:
            QMessageBox.warning(self.gui, "Warning", "No object selected.")
            return False

        self.obj_list = [cmds.listRelatives(sel, shapes=True, fullPath=True) for sel in selection]
        if not self.obj_list:
            QMessageBox.warning(self.gui, "Warning", "Selected object is not a shape.")
            return False

        self.obj_in.setText(", ".join(selection))
        self.obj_list = selection
        return True

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


#-----------------------------------------------------------------------------------------------------------------------

tool = Selection()
tool.gui.show()