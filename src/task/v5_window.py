#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: v5_window
from src.common.utils.geometry import Box
from src.common.utils.windows import WindowExec
from src.task.base_window import BaseWindow


class V5Window(BaseWindow):
    def __init__(self):
        we_v5 = WindowExec("V5 程序多开器 0.1 Beta", "#32770", r"C:\Tools\V5\V5.exe")
        super().__init__(we_v5)

    def open_onmyoji(self):
        # 前提：v5多开器已选择C:\Program Files (x86)\Onmyoji\Launch.exe作为程序路径参数

        # v5上"打开隔离程序"按钮参数，大小，相对于窗口左上角的坐标
        v5_open_button = Box(195, 124, 95, 32)
        self.click_sub_element(v5_open_button)
