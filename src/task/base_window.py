#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved
#
# Function: base_window
import os.path
import subprocess
import time

import pyautogui

from src.common.utils.geometry import to_box, to_rectangle, box_offset, Rectangle, Box, random_center_default
from src.common.utils.logger import get_log
from src.common.utils.windows import WindowExec, check_window, close_window, close_window_by_hwnd, \
    get_window_information, set_window_front, draw_on_desktop, click

log = get_log()
stat_log = get_log('statistic')


def statistic(func):
    """计算执行时间的装饰器，传入参数为装饰的函数或方法"""
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        stat_log.info('%s() execute time: %ds' % (func.__name__, end - start))
        return res

    return wrapper


class BaseWindow:
    """
    基础窗口操作
    """

    def __init__(self, window_exec: WindowExec):
        # 入参
        self.window_exec = window_exec

        # 窗口参数
        self.window_info = None
        self.hwnd = -1
        self.rect = None
        self.box = None

    @staticmethod
    def sleep(duration, message=None) -> None:
        """
        对time.sleep()方法进行封装，提供sleep时的日志输出
        :param duration: sleep时长
        :param message: sleep时的日志
        :return: None
        """
        if message is not None:
            log.debug(F"sleep {duration} seconds for {message}")
        time.sleep(duration)

    def open(self) -> None:
        """
        根据window_exec，调用系统命令打开窗口
        :return: None
        """
        flag, window_info_list = check_window(self.window_exec)
        if not flag:
            log.info(F"window [{self.window_exec.title}] will be open.")
            subprocess.Popen(self.window_exec.exec)
            self.sleep(3, F"waiting window [{self.window_exec.title}] opened")
            _, window_info_list = check_window(self.window_exec)

        # 只有一个v5窗口
        self.hwnd = window_info_list[0].hwnd
        self.update()

    def close(self, close_all=False) -> None:
        """
        关闭窗口
        :param close_all: 是否关闭所有窗口
        :return: None
        """
        close_window(self.window_exec) if close_all else close_window_by_hwnd(self.hwnd)
        self.sleep(1)

    def update(self) -> None:
        """
        更新窗口位置信息
        :return: None
        """
        self.window_info = get_window_information(self.hwnd)
        self.hwnd = self.window_info.hwnd
        self.rect = self.window_info.rectangle
        self.box = to_box(self.rect)

    def draw_rectangle(self, rectangle=None):
        """
        绘制窗口上的矩形位置
        :param rectangle: 待绘制的矩形位置
        :return: None
        """
        _rectangle = rectangle if rectangle is not None else self.rect
        draw_on_desktop(_rectangle)

    def cal_sub_element(self, sub_box: Box) -> Rectangle:
        """
        计算当前窗口上子元素的位置
        :param sub_box: 子元素相对于当前窗口的相对坐标
        :return: 子元素在桌面窗口中的绝对坐标
        """
        absolute_box = box_offset(sub_box, self.rect.left, self.rect.top)
        sub_rect = to_rectangle(absolute_box)

        # 绘制元素位置
        set_window_front(self.hwnd)
        self.draw_rectangle(sub_rect)

        return sub_rect

    def click_sub_element(self, sub_box: Box) -> Rectangle:
        """
        计算窗口上子元素的位置，并点击子元素的中心点
        :param sub_box: 子元素相对于当前窗口的相对坐标
        :return: 子元素在桌面窗口中的绝对坐标
        """
        sub_rect = self.cal_sub_element(sub_box)

        # 左键单击元素中心位置
        click(random_center_default(sub_rect))
        return sub_rect

    @statistic
    def find_match_picture(self, fp: str | list, sr=None, cf=.8, ic=True) -> bool:
        """
        查找匹配的图片并点击图片中心
        :param fp: filepath of picture，图片文件路径，字符串路径或数组
        :param sr: search region，搜索范围，默认为当前窗口范围
        :param cf: confidence，图片匹配时的置信度
        :param ic: is_click，是否要点击
        :return: 图片是否匹配成功
        """
        _region = self.rect if sr is None else sr
        _fp = fp if isinstance(fp, str) else os.path.join(*fp)

        pic_box = pyautogui.locateOnScreen(_fp, region=_region, confidence=cf)
        log.debug(f"matched box is {pic_box}, picture is {os.path.basename(_fp)} in region {_region}")
        if pic_box:
            rect_matched = to_rectangle(pic_box)
            if ic:
                # 左键单击匹配图片的中心位置
                click(random_center_default(rect_matched))
            return True
        else:
            return False
