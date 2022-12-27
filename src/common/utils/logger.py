#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: logger

import logging

log_fmt = '%(asctime)s|%(filename)s|%(funcName)s:%(lineno)d|%(levelname)s| %(message)s'
formatter = logging.Formatter(log_fmt)
logging.basicConfig(level=logging.INFO, format=log_fmt)


def get_log(name='root'):
    __logger = logging.getLogger(name)

    if len(__logger.handlers) == 0:
        __logger.setLevel(level=logging.DEBUG)

        # log file handler
        fp_log = __file__.split('src')[0] + name + ".log"
        handler = logging.FileHandler(fp_log, encoding='UTF-8')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        __logger.addHandler(handler)

    return __logger
