#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: ArknightsTask
import json

import yaml

from src.common.definition import MPParser
from src.common.log.logger import get_log
from src.task.task_api import Handler

log = get_log()


class ArknightsHandler(Handler):

    def __init__(self, **kwargs):
        super(ArknightsHandler, self).__init__()

    def start_daily(self, fp_config):
        task = "arknights daily task"
        self.start(fp_config, ["arknights", "daily"], task)
