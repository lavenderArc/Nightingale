#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: logger

import logging

log_fmt = '%(asctime)s %(process)d|%(thread)d[%(filename)s %(funcName)s:%(lineno)d][%(levelname)s] %(message)s'
formatter = logging.Formatter(log_fmt)
logging.basicConfig(level=logging.INFO, format=log_fmt)


def get_log(name='root'):
    __logger = logging.getLogger(__name__)
    __logger.setLevel(level=logging.INFO)

    # log file handler
    handler = logging.FileHandler(name + ".log")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    __logger.addHandler(handler)

    return __logger
