#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: ArknightsTask
import json
import os
import time

from src.common.utils.geo_api import GeoUtils
from src.common.log.logger import get_log
from src.task.task_api import Task

log = get_log()


def get_time():
    return time.asctime()


class ArknightsTask(Task):
    MISSION_RESULTS = "mission_results"
    START_OPERATION_RUN = "start_operation_run"

    def __init__(self, **kwargs):
        super(ArknightsTask, self).__init__()
        self.__pics = kwargs.get("pics") or []
        self.__pic_dir = kwargs.get("pic_dir")
        self.__pic_sets = []
        # TODO: 文件存在性检查

        self.__random_size = kwargs.get("random_size") or (10, 5)
        self.__dura = kwargs.get('dura') or 1

        self.__result_mission_fail_times = 0

    def is_mission_result(self, pic_name):
        return pic_name.__contains__(self.MISSION_RESULTS)

    def is_start_operation_run(self, pic_name):
        return pic_name.__contains__(self.START_OPERATION_RUN)

    def __update_dirs(self):
        tmp_files = [os.path.join(self.__pic_dir, x) for x in os.listdir(self.__pic_dir)]
        tmp_files = [x for x in tmp_files if os.path.isfile(x)]

        tmp_files = set(tmp_files).union(self.__pics)
        tmp_files = list(tmp_files)
        tmp_files.sort()

        update_results = set(tmp_files) - set(self.__pic_sets)
        if update_results:
            log.info(F"picture sets updated, \n{json.dumps(list(update_results), indent=4)}")
            self.__pic_sets = tmp_files

    def start(self):
        while True:
            self.run_one_turn()

    def run_one_turn(self):
        self.__update_dirs()
        for pic in self.__pic_sets:
            pic_name = os.path.basename(pic)
            self.sleep(self.__dura)

            if os.path.exists(pic):
                pic_location = self.match(pic)
            else:
                continue
            if pic_location is not None:
                if self.is_mission_result(pic_name):
                    pic_center = self.screen_center
                    self.__result_mission_fail_times = 0
                else:
                    pic_center = GeoUtils.box_center(pic_location)
                self.click(pic_center, self.__random_size)
                if self.is_start_operation_run(pic_name):
                    self.sleep(90)
                continue
