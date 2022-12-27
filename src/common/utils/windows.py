#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: windows
import time
from collections import namedtuple

import win32api
import win32con
import win32gui
import win32ui

from src.common.utils.logger import get_log
from src.common.utils.geometry import Rectangle, Point, Box

WindowInformation = namedtuple('WindowInformation', ['title', 'clazz', 'hwnd', 'rectangle'])
WindowExec = namedtuple('WindowExec', ['title', 'clazz', 'exec'])

log = get_log()


def get_all_windows() -> list[WindowInformation]:
    """
    获取所有的窗口
    :return:
    """
    all_windows = []
    hwnd_list = []
    win32gui.EnumWindows(lambda handle_window, param: param.append(handle_window), hwnd_list)
    for hwnd in hwnd_list:
        window_information = get_window_information(hwnd)
        all_windows.append(window_information)
    return all_windows


def get_window_information(hwnd: int) -> WindowInformation:
    """
    获取窗口信息
    :param hwnd: 窗口句柄
    :return:
    """
    clazz = win32gui.GetClassName(hwnd)
    title = win32gui.GetWindowText(hwnd)
    region = win32gui.GetWindowRect(hwnd)
    rect = Rectangle(region[0], region[1], region[2], region[3])
    return WindowInformation(title, clazz, hwnd, rect)


def draw_rectangle(draw_hwnd, rect, hold_on=1) -> None:
    """
    在一段时间内对一个矩形进行绘制
    :param draw_hwnd: 用于绘制矩形的窗口句柄
    :param rect: 待绘制的矩形，相对于绘制矩形的窗口坐标
    :param hold_on: 持续时间
    :return:
    """
    h_dc = win32gui.GetDC(draw_hwnd)
    h_pen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(255, 0, 255))  # 定义框颜色
    old_pen = win32gui.SelectObject(h_dc, h_pen)
    h_brush = win32gui.GetStockObject(win32con.NULL_BRUSH)  # 定义透明画刷
    old_brush = win32gui.SelectObject(h_dc, h_brush)

    dc_obj = win32ui.CreateDCFromHandle(h_dc)
    begin_draw_time = time.time()
    while True:
        win32gui.InvalidateRect(draw_hwnd, rect, True)  # Refresh the entire monitor
        dc_obj.Rectangle(rect)
        if time.time() - begin_draw_time > hold_on:
            break

    # 还原并释放资源
    win32gui.SelectObject(h_dc, old_pen)
    win32gui.SelectObject(h_dc, old_brush)
    win32gui.DeleteObject(h_pen)
    win32gui.DeleteObject(h_brush)
    win32gui.ReleaseDC(draw_hwnd, h_dc)


def draw_on_desktop(rect: Rectangle) -> None:
    """
    在桌面窗口中绘制矩形
    :param rect: 待绘制的矩形
    :return:
    """
    monitor_hwnd = win32gui.GetDesktopWindow()
    draw_rectangle(monitor_hwnd, (rect.left, rect.top, rect.right, rect.bottom))


def set_window_front(hwnd):
    """
    将窗口前置
    :param hwnd: 窗口句柄
    :return:
    """
    # ref: https://segmentfault.com/a/1190000040406710
    if win32gui.IsIconic(hwnd):
        # print("iconic")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(3)  # 有动画过程，等待2s
    else:
        # print("not iconic")
        win32gui.SetForegroundWindow(hwnd)


def close_window(window_exec: WindowExec) -> None:
    """
    关闭窗口
    :param window_exec: 窗口
    :return:
    """
    hwnd = win32gui.FindWindow(window_exec.clazz, window_exec.title)
    if hwnd > 0:
        log.info(f"close v5 window by hwnd {hwnd}")
        close_window_by_hwnd(hwnd)


def close_window_by_hwnd(hwnd) -> None:
    """
    send close window message to window
    :param hwnd:
    :return:
    """
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def check_window(window_exec: WindowExec) -> (bool, list[int]):
    all_windows = get_all_windows()
    tmp = [x for x in all_windows if x.clazz == window_exec.clazz and x.title == window_exec.title]
    if tmp.__len__():
        log.debug(F"{window_exec.title} window has open, windows: {[(x.hwnd, x.rectangle) for x in tmp]}")
        return True, tmp
    else:
        log.info(F"{window_exec.title} windows has not open")
        return False, None


def click(p: Point) -> None:
    log.debug(f"click at position {p}")
    win32api.SetCursorPos(p)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def move_window(hwnd: int, b: Box) -> None:
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, b.left, b.top, b.width, b.height, win32con.SWP_SHOWWINDOW)


def find_window(window_exec: WindowExec):
    return win32gui.FindWindow(window_exec.clazz, window_exec.title)


def send_enter_to_window(hwnd, vk=win32con.VK_RETURN):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk, 0)
