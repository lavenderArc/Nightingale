#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: task_api
import json
import os
from datetime import datetime
from typing import List

import pyautogui
import yaml

from src.common.definition import MatchPic, MPParser
from src.common.log.logger import get_log
from src.common.utils.geo_api import GeoUtils

log = get_log()


class Handler:
    def __init__(self, **kwargs):
        self.screen_size = pyautogui.size()
        self.screen_center = GeoUtils.size_center(self.screen_size)
        self.assets_dir = kwargs.get("assets_dir")
        self.window_region = kwargs.get("window_region")

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

    def match(self, fp_pic, confidence=.9, region=None):
        """
        match fore desktop by picture filepath
        :param fp_pic: picture filepath
        :param confidence: confidence
        :param region: region
        :return: matched picture box or None
        """
        if region:
            pic_box = pyautogui.locateOnScreen(fp_pic, confidence=confidence, region=region)
        else:
            pic_box = pyautogui.locateOnScreen(fp_pic, confidence=confidence)
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

    def start(self, fp_config, keys, task):
        with open(fp_config, 'r') as file:
            content = yaml.safe_load(file)

            args = content.get(keys[0])
            for key in keys[1:]:
                args = args.get(key)
            parser = MPParser(**args)
            log.info(parser)

        last_time, current_time = None, None
        count, time_series = 0, []
        while True:
            self.start_one_turn(parser.pics, task)
            if last_time:
                current_time = datetime.now()
                count += 1
                cost_time = (current_time - last_time).seconds
                time_series.append(cost_time)
                log.info(F"this turn uses {cost_time} seconds, avg {sum(time_series) / count} seconds, {count} times")
                last_time = current_time
            else:
                last_time = datetime.now()

    def start_one_turn(self, lst: List[MatchPic], task="default"):
        scan_dura = 1
        i = 0
        total = len(lst)
        while i < total:
            match_pic = lst[i]
            pic_box = self.match(match_pic.fp, match_pic.confidence, match_pic.scan_region)
            if pic_box:
                log.info(F"find at {pic_box}, {task} progress {i + 1}/{total}.")
                if not match_pic.skip_click:
                    pic_pos = GeoUtils.box_center(pic_box)
                    self.click(pic_pos, match_pic.buffer_region)
                if match_pic.pause_time > 0:
                    self.sleep(match_pic.pause_time)

                # to next
                i += 1
            else:
                self.sleep(scan_dura)

            # to next circular
            # i += 1

        pass
