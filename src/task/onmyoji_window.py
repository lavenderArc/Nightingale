#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: onmyoji_windows
import itertools
import os
import time

import pyautogui

from src.common.utils.geometry import Box, to_rectangle, Point, box_offset
from src.common.utils.logger import get_log
from src.common.utils.windows import check_window, WindowExec, move_window, find_window, close_window_by_hwnd, \
    send_enter_to_window, set_window_front
from src.task.base_window import BaseWindow, statistic
from src.task.v5_window import V5Window

log = get_log()


class OnmyojiWindow(BaseWindow):
    def __init__(self):
        """
        onmyoji窗口
        """
        we_onmyoji = WindowExec("阴阳师-网易游戏", "Win32Window", r"C:\Program Files (x86)\Onmyoji\Launch.exe")
        super().__init__(we_onmyoji)

        self.dir_onmyoji = os.path.join(__file__.split('task')[0], 'assets', 'Onmyoji')
        self.partner = None
        self.account = ""

    def open(self):
        """
        通过v5多开器打开一个onmyoji窗口，
        关键操作前没有置顶，过程中不可以点击其他窗口
        :return: 打开的窗口
        """
        # 1.打开v5多开器
        v5w = V5Window()
        v5w.open()

        # 2.打开Onmyoji
        v5w.open_onmyoji()
        self.sleep(10, "waiting window onmyoji opened")

        # 3.检查打开完成
        # TODO：有版本更新的场景
        fp_pic = [self.dir_onmyoji, 'login', 'wy_title.png']
        if not self.wait_picture_appear(fp_pic):
            log.error(F"not found match pic filepath {fp_pic[-1]}")
            raise Exception("open onmyoji window failed.")

        # 4.新打开的窗口为第一个窗口（保持基类窗口的行为）
        flag, window_info_list = check_window(self.window_exec)
        if flag:
            self.hwnd = window_info_list[0].hwnd
            self.update()
        else:
            raise Exception("open onmyoji window by v5 failed.")

    def close(self, close_all=False) -> None:
        """
        关闭Onmyoji窗口
        :param close_all: 是否关闭所有窗口，默认只关闭当前窗口
        :return: None
        """

        def __close(h):
            log.info(f"close onmyoji window by hwnd {h}")
            close_window_by_hwnd(h)

            # 等待退出游戏窗口出现，发送enter消息
            self.sleep(1, "waiting 'exit game' message box appeared")
            we_exit_game = WindowExec("退出游戏", "#32770", "<click>")  # 关闭游戏时确认窗口
            hwnd_exit_game = find_window(we_exit_game)
            send_enter_to_window(hwnd_exit_game)
            self.sleep(3, "waiting onmyoji window closed")

        if not close_all:
            __close(self.hwnd)
        else:
            hwnd = find_window(self.window_exec)
            while hwnd > 0:
                __close(hwnd)
                hwnd = find_window(self.window_exec)

    def init_by_hwnd(self, hwnd: int, account: str) -> None:
        """
        通过句柄初始化Onmyoji窗口
        :param hwnd: 窗口句柄
        :param account: 账号
        :return: None
        """
        self.hwnd = hwnd
        self.account = account
        self.update()

    def adjust(self, pos: Point):
        """
        调整窗口位置，大小保持当前的
        :param pos: 窗口新的左上角位置
        :return: None
        """
        # 调整窗口位置
        box_new = Box(*pos, self.box.width, self.box.height)
        log.info(F"adjust window position to {box_new}")
        move_window(self.hwnd, box_new)
        self.update()

    @statistic
    def wait_picture_appear(self, fp: str | list, region=None, timeout=120, interval=1, is_draw=True) -> (bool, Box):
        """
        等待待匹配的图片出现
        :param fp: 图片路径
        :param region: 扫描范围，默认为None，扫描整个桌面，性能低，慎用于循环中
        :param timeout: 超时时间，默认120s
        :param interval: 扫描间隔，默认1s
        :param is_draw: 是否绘制匹配到的图片位置
        :return: 匹配成功标识，匹配到的图片位置
        """
        begin_time = time.time()
        _fp = fp if isinstance(fp, str) else os.path.join(*fp)

        while time.time() - begin_time <= timeout:
            if region:
                picture_box = pyautogui.locateOnScreen(_fp, region)
            else:
                picture_box = pyautogui.locateOnScreen(_fp)
            if picture_box:
                rect_picture = to_rectangle(picture_box)
                if is_draw:
                    self.draw_rectangle(rect_picture)
                log.info(F"found matched picture in position {rect_picture}, filepath {os.path.basename(_fp)}")
                return True, rect_picture
            else:
                # 停一会再扫描
                self.sleep(interval, f"waiting matched picture appear, filepath {os.path.basename(_fp)}")
        return False, None

    def login(self, account: str):
        """
        登录指定账号
        :param account: 账号，需要先获取登录前账号的截图和登录后的名染截图
        :return: None
        """

        def switch_account():
            # 点击输入账号的位置
            box_input_account = Box(309, 221, 299, 69)
            self.click_sub_element(box_input_account)
            self.sleep(1, "waiting onmyoji select box expand")

            # 选择要登录的账号
            box_select_account = Box(309, 290, 299, 129)
            rectangle_select_account = self.cal_sub_element(box_select_account)

            # 查找匹配位置
            fp_account = [self.dir_onmyoji, 'privacy', 'account_' + account + '.png']
            self.find_match_picture(fp_account, rectangle_select_account)
            self.sleep(1, "waiting onmyoji select box confirm")

        def log_onmyoji():
            # 点击"进入游戏"按钮登录onmyoji
            box_enter_game = Box(309, 321, 299, 41)
            self.click_sub_element(box_enter_game)
            self.sleep(5, "waiting onmyoji login to inner login")

            # 查找匹配位置
            fp_game_8_years = [self.dir_onmyoji, 'login', 'game_8+.png']
            if not self.wait_picture_appear(fp_game_8_years):
                log.error(F"not found match pic filepath {fp_game_8_years[-1]}")
                raise Exception("login failed")

        def log_server():
            # 点击"进入游戏"按钮进入庭院
            box_enter_game_inner = Box(400, 436, 120, 36)
            self.click_sub_element(box_enter_game_inner)
            self.sleep(5, "waiting onmyoji enter courtyard")

            # 检查名染
            fp_mr = [self.dir_onmyoji, 'privacy', 'mr_' + account + '.png']
            if not self.wait_picture_appear(fp_mr):
                log.error(F"not found match pic filepath {fp_mr[-1]}")
                raise Exception("enter failed")
            self.account = account

        # 登录步骤
        switch_account()
        log_onmyoji()
        log_server()

    def checkin(self):
        pass

    def to_exploration(self):
        """
        到探索界面
        :return:
        """
        set_window_front(self.hwnd)
        self.sleep(1, "waiting window stable")

        fp_exploration = [self.dir_onmyoji, 'courtyard', 'latin_explore_472-126.png']
        self.find_match_picture(fp_exploration)
        self.sleep(3, "waiting for turn around")

    def invite(self, other: object):
        """
        邀请好友加入
        :param other: onmyoji窗口对象
        :return:
        """
        self.partner = other

    def start_souls(self, turns=100):

        def start():
            set_window_front(self.hwnd)
            self.sleep(1, "waiting window stable")

            # 探索底部御魂副本
            self.find_match_picture([self.dir_onmyoji, 'soul', 'footer_soul_124-476.png'])
            self.sleep(1, "waiting window stable")

            # 八岐大蛇副本
            self.find_match_picture([self.dir_onmyoji, 'soul', 'slot_orochi_50-128.png'])
            self.sleep(1, "waiting window stable")

            # 组队
            self.find_match_picture([self.dir_onmyoji, 'soul', 'create_team00_button_675-466.png'])
            self.sleep(1, "waiting window stable")

            # 创建队伍
            self.find_match_picture([self.dir_onmyoji, 'soul', 'create_team_button_706-457.png'])
            self.sleep(1, "waiting window stable")

            # 创建
            self.find_match_picture([self.dir_onmyoji, 'soul', 'create_button_583-431.png'])
            self.sleep(1, "waiting window stable")

            # 邀请（队伍中的加号）
            self.find_match_picture([self.dir_onmyoji, 'soul', 'invite_button_420-170.png'])
            self.sleep(5, "waiting window stable")

            # 好友中的绘梨衣（需要在线且排名考前）
            self.find_match_picture([self.dir_onmyoji, 'privacy', 'partner_' + self.partner.account + '.png'])
            self.sleep(1, "waiting window stable")

            # 确认邀请
            self.find_match_picture([self.dir_onmyoji, 'soul', 'invite_ok_button_.png'])
            self.sleep(2, "waiting window stable")

            self.partner.accept_invite_initial()

        @statistic
        def one_turn():
            # 开始战斗
            self.find_match_picture([self.dir_onmyoji, 'soul', 'soul_attack_button.png'])
            self.sleep(20, 'waiting souls finish.')

            # 战斗结束
            fp_xiu = [self.dir_onmyoji, 'soul', 'soul_invitees_results_xiu.png']
            flag, _ = self.wait_picture_appear(fp=fp_xiu, is_draw=False)
            if flag:
                self.find_match_picture(fp_xiu)

            flag, _ = self.partner.wait_picture_appear(fp=fp_xiu, is_draw=False)
            if flag:
                self.partner.find_match_picture(fp_xiu)

            # 奖励结算
            fp_awards = [self.dir_onmyoji, 'soul', 'soul_invitees_results_awards.png']
            flag, _ = self.wait_picture_appear(fp=fp_awards, is_draw=False)
            if flag:
                self.find_match_picture(fp_awards)

            flag, _ = self.partner.wait_picture_appear(fp=fp_awards, is_draw=False)
            if flag:
                self.partner.find_match_picture(fp_awards)
            self.sleep(2, 'waiting turn around.')

        def first_round():
            one_turn()
            # 默认邀请
            self.invite_always()
            self.sleep(2, 'waiting')

            # 队友默认接受
            self.partner.accept_invite_always()
            self.sleep(2, 'waiting')

        # 打开加成
        self.click_soul_buff()
        self.partner.click_soul_buff()

        start()
        first_round()
        for i in range(turns - 1):
            one_turn()
            log.info(f"run turn {i + 2}/{turns}")

        # 退出组队
        self.exit_team()
        self.partner.exit_team()

        # 关闭加成
        self.click_soul_buff()
        self.partner.click_soul_buff()

    def exit_team(self):
        exit_box = Box(25, 42, 32, 32)
        self.click_sub_element(exit_box)
        self.sleep(1, "waiting ok button")

        self.find_match_picture([self.dir_onmyoji, 'soul', 'invite_always_ok.png'])
        self.sleep(1, "waiting exit souls.")

    def click_soul_buff(self):
        buff_box = Box(305, 45, 24, 32)
        soul_buffer_box = Box(550, 175, 84, 24)

        # 打开加成
        self.click_sub_element(buff_box)
        self.sleep(1, 'waiting buff expand.')
        self.click_sub_element(soul_buffer_box)
        self.sleep(1, 'waiting buff clicked.')
        self.click_sub_element(buff_box)
        self.sleep(1, 'waiting buff collapse.')

    def accept_invite_initial(self):
        log.info("accept invite message")
        set_window_front(self.hwnd)

        fp_accept = [self.dir_onmyoji, 'soul', 'accept_invitation_button.png']
        self.find_match_picture(fp_accept)
        self.sleep(1, "waiting window stable")

        pass

    def invite_always(self):
        # 战斗结束
        fp_invite = [self.dir_onmyoji, 'soul', 'invite_always.png']
        flag, _ = self.wait_picture_appear(fp=fp_invite, is_draw=False)
        if flag:
            self.find_match_picture(fp_invite)
            self.sleep(1, 'waiting')
            fp_invite_ok = [self.dir_onmyoji, 'soul', 'invite_always_ok.png']
            self.find_match_picture(fp_invite_ok)
        pass

    def accept_invite_always(self):
        fp_invite_always = [self.dir_onmyoji, 'soul', 'accept_invite_always.png']
        self.find_match_picture(fp_invite_always)
        self.sleep(1, "waiting window stable")
        pass

    @statistic
    def open_realm_raid(self):
        set_window_front(self.hwnd)
        self.sleep(1, "waiting window stable")

        fp_realm_raid_icon = [self.dir_onmyoji, 'realm', 'realm_footer_icon.png']
        self.find_match_picture(fp_realm_raid_icon)
        self.sleep(1, "waiting window stable")

        if self.is_in_realm_raid():
            log.info("in personal realm.")
        else:
            log.info("not in personal realm.")
            raise Exception("not in personal realm.")

    def is_in_realm_raid(self) -> bool:
        fp_realm_raid_this_week = [self.dir_onmyoji, 'realm', 'personal_this_week_title.png']
        flag, _ = self.wait_picture_appear(fp_realm_raid_this_week, timeout=10)
        return flag

    @statistic
    def realm_raid(self):
        # 突破资源目录
        # 个人突破内圈区域
        index_0_box = Box(112, 136, 224, 84)
        span_horizontal = 234
        span_vertical = 95

        result_success = 0
        result_tickets_used = 1
        result_unknown = -1

        def check_status(pos: Point):
            horizontal_offset = self.rect.left + span_horizontal * pos.x
            vertical_offset = self.rect.top + span_vertical * pos.y
            realm_raid_area = box_offset(index_0_box, horizontal_offset, vertical_offset)
            # realm_raid_rect = to_rectangle(realm_raid_area)
            # self.draw_rectangle(realm_raid_rect)

            # 1. 检查当前结界是否已攻击过
            attack_status = "initial"
            if self.find_match_picture([self.dir_onmyoji, 'realm', 'realm_success_marker.png'], sr=realm_raid_area,
                                       ic=False, cf=.7):
                attack_status = "success"
            elif self.find_match_picture([self.dir_onmyoji, 'realm', 'realm_failed_marker_small.png'],
                                         sr=realm_raid_area, ic=False):
                attack_status = "failed"

            metal_counter = -1
            if attack_status == 'initial':
                metal_counter = 0
                for i in range(5, 0, -1):
                    if self.find_match_picture([self.dir_onmyoji, 'realm', f'orders_{i}.png'], sr=realm_raid_area,
                                               cf=.95, ic=False):
                        metal_counter = i
                        break
            log.info(f"personal realm {pos} has {attack_status} history, orders count: {metal_counter}.")
            return attack_status, metal_counter

        def enter_to_attack(pos: Point):
            log.info(f"enter to attack: {pos}")
            # 个人突破点击区域
            index_0_click_box = Box(175, 136, 161, 84)
            absolute_box_sub_click = box_offset(index_0_click_box, span_horizontal * pos.x, span_vertical * pos.y)
            self.click_sub_element(absolute_box_sub_click)
            self.sleep(1, "waiting personal realm expand")

            # 2.点击进攻
            attack_box = Box(232, 283, 94, 44)
            absolute_box_sub_attack = box_offset(attack_box, span_horizontal * pos.x, span_vertical * pos.y)
            self.click_sub_element(absolute_box_sub_attack)
            self.sleep(7, "waiting personal realm enter")

        def end_with_success():
            fp_awards = [self.dir_onmyoji, 'soul', 'soul_invitees_results_awards.png']
            is_find, rect = self.wait_picture_appear(fp_awards)
            if is_find:
                self.find_match_picture(fp_awards)

        def exit_for_failed():
            # 点击退出
            exit_realm_box = Box(20, 42, 24, 24)
            self.click_sub_element(exit_realm_box)
            self.sleep(2, "waiting exit realm message box appear")

            # 点击确认
            exit_realm_ok_box = Box(483, 307, 94, 44)
            self.click_sub_element(exit_realm_ok_box)
            self.sleep(5, "waiting failed result")

            # 失败结果页面
            failed_box = Box(294, 130, 88, 56)
            self.click_sub_element(failed_box)
            self.sleep(3, "waiting for exit realm ")

        def check_current_awards():
            self.sleep(1, "waiting window stable.")
            set_window_front(self.hwnd)

            fp_attacked_2 = [self.dir_onmyoji, 'realm', 'attacked_2.png']
            if self.find_match_picture(fp_attacked_2):
                return 2

            fp_attacked_5 = [self.dir_onmyoji, 'realm', 'attacked_5.png']
            if self.find_match_picture(fp_attacked_5):
                return 5

            fp_attacked_8 = [self.dir_onmyoji, 'realm', 'attacked_8.png']
            if self.find_match_picture(fp_attacked_8):
                return 8
            return -1

        def check_0_30() -> bool:
            self.sleep(1, "waiting window stable.")

            return self.find_match_picture(fp=[self.dir_onmyoji, 'realm', 'realm_tickets_0_30.png'], cf=.95)

        def attack_from_0_9():
            # 正向攻破这一页的结界
            for pair in itertools.product(range(3), range(3)):
                if check_0_30():
                    log.info("realm paid tickets used.")
                    return result_tickets_used

                fixed_pos = Point(*(pair[::-1]))
                if fixed_pos == (2, 2):
                    log.error("exit by 4 times, then attack.")
                    enter_to_attack(fixed_pos)
                    for i in range(4):
                        exit_for_failed()
                        enter_to_attack(fixed_pos)
                    end_with_success()

                    # 9次攻击的结果
                    end_with_success()
                    return result_success

                status, _ = check_status(fixed_pos)
                if status == 'initial':
                    current_awards = check_current_awards()
                    enter_to_attack(fixed_pos)
                    end_with_success()
                    if current_awards in [2, 5, 8]:
                        end_with_success()
                else:
                    log.info(F"personal realm {fixed_pos} has been attacked.")

        def attack_from_9_0(for_success=True):
            # 反向攻破这一页的结界
            for pair in itertools.product(range(3)[::-1], range(3)[::-1]):
                if check_0_30():
                    log.info("realm paid tickets used.")
                    return result_tickets_used

                fixed_pos = Point(*(pair[::-1]))
                status, _ = check_status(fixed_pos)

                if status == 'initial':
                    current_awards = check_current_awards()
                    enter_to_attack(fixed_pos)
                    if for_success:
                        end_with_success()
                        if current_awards in [2, 5, 8]:
                            end_with_success()
                    else:
                        exit_for_failed()
                else:
                    log.info(F"personal realm {fixed_pos} has been attacked.")
            if not for_success:
                log.info("click refresh button.")
                # 点击刷新
                self.sleep(2, 'waiting window stable')
                self.find_match_picture(fp=[self.dir_onmyoji, 'realm', 'realm_refresh.png'])
                self.sleep(2, 'waiting ok button')
                self.find_match_picture(fp=[self.dir_onmyoji, 'realm', 'invite_always_ok.png'])
                self.sleep(2, 'waiting realm refresh success')

        set_window_front(self.hwnd)
        attack_func = attack_from_0_9
        status22, _ = check_status(Point(2, 2))
        if status22 == 'success':
            attack_func = attack_from_9_0
        while True:
            log.info(f"attack realm paid by {attack_func.__name__}")
            if attack_func() == result_tickets_used:
                break

            # switch attack orders by last function
            if attack_func.__name__ == attack_from_9_0.__name__:
                attack_func = attack_from_0_9
            elif attack_func.__name__ == attack_from_0_9.__name__:
                attack_func = attack_from_9_0
            else:
                raise Exception("unknown params")

    def accept_bounty(self, is_accept=True):
        scan_area = Box(580, 300, 55, 125)
        fp_accept = [self.dir_onmyoji, 'courtyard', 'bounty_accept.png']
        fp_refuse = [self.dir_onmyoji, 'courtyard', 'bounty_refuse.png']
        if is_accept:
            if self.find_match_picture(fp_accept):
                log.warning("accepted bounty invitation")
        else:
            if self.find_match_picture(fp_refuse):
                log.warning("refused bounty invitation")
