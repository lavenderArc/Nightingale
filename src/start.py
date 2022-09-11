#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: start
import os
import sys

from src.task.arknights_api import ArknightsTask
from src.common.log.logger import get_log

log = get_log()

if __name__ == '__main__':
    run_path = os.path.dirname(sys.argv[0])
    example = {
        "pic_dir": os.path.join(run_path, "assets", "daily")
    }

    task = ArknightsTask(**example)
    try:
        log.info("start...")
        task.start()
    except Exception as e:
        print(e)
