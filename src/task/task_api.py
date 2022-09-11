#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: task_api
import os

import pyautogui

from src.common.log.logger import get_log
from src.common.utils.geo_api import GeoUtils

log = get_log()


class Task:
    def __int__(self):
        self.screen_size = pyautogui.size()
        self.screen_center = GeoUtils.size_center(self.screen_size)

    def click(self, position, buffer):
        """
        mouse left click at postion with random buffer
        :param position: position (x, y)
        :param buffer: buffer (random_x, random_y)
        :return: None
        """
        mixed_pos, mixed_val = GeoUtils.random_position(position, buffer)
        pyautogui.click(mixed_pos)
        log.info(F"clicked at position {mixed_pos} with random {mixed_val}.")

    def match(self, fp_pic):
        """
        match fore desktop by picture filepath
        :param fp_pic: picture filepath
        :return: matched picture box or None
        """
        pic_box = pyautogui.locateOnScreen(fp_pic)
        if pic_box:
            log.info(F"captured {os.path.basename(fp_pic)}.")
            return pic_box
        else:
            log.info(F"not captured {os.path.basename(fp_pic)}.")

    def sleep(self, dura):
        """
        thread sleep for dura seconds
        :param dura: sleep duration (unit: seconds)
        :return: None
        """
        pyautogui.sleep(dura)
