#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: definition
import json
import os
from collections import namedtuple

import yaml

Rect = namedtuple('Rect', ['left', 'top', 'width', 'height'])

BufferRegion = namedtuple('BufferRegion', ['left', 'right', 'down', 'up'])

BufferRegionRect = namedtuple('BufferRegionRect', ['width', 'height'])


class Const:
    PAUSE_TIME = 1
    CONFIDENCE = .9
    SCAN_REGION = None
    SKIP_CLICK = False


class MatchPic:
    def __init__(self, fp_pic, buffer_region, pause_time=Const.PAUSE_TIME, confidence=Const.CONFIDENCE,
                 scan_region=Const.SCAN_REGION, skip_click=Const.SKIP_CLICK):
        self.fp = fp_pic
        self.buffer_region = buffer_region
        self.pause_time = pause_time
        self.confidence = confidence
        self.scan_region = scan_region
        self.skip_click = skip_click

    def __str__(self):
        return {
            "fp": self.fp,
            "buffer_region": self.buffer_region,
            "pause_time": self.pause_time,
            "confidence": self.confidence,
            "scan_region": self.scan_region,
            "skip_click": self.skip_click,
        }


class MPParser:
    def __init__(self, **kwargs):
        self.pics = []

        assets_dir = r'C:\Users\lijianye\Code\Nightingale\src\assets'
        work_dir = kwargs.get("word_dir")
        workflow = kwargs.get("workflow")
        for job in workflow:
            fp_pic = os.path.join(assets_dir, *work_dir, job.get("fp_pic"))
            buffer_region = self.transform_region(job.get("buffer_region"))
            pause_time = job.get("pause_time") or Const.PAUSE_TIME
            confidence = job.get("confidence") or Const.CONFIDENCE
            scan_region = self.transform_region(job.get("scan_region")) or Const.SCAN_REGION
            skip_click = job.get("skip_click") or Const.SKIP_CLICK
            mp = MatchPic(
                fp_pic=fp_pic,
                buffer_region=buffer_region,
                pause_time=pause_time,
                confidence=confidence,
                scan_region=scan_region,
                skip_click=skip_click
            )
            self.pics.append(mp)
        pass

    def transform_region(self, region):
        if region is None:
            return None
        if len(region) == 2:
            return BufferRegionRect(*region)
        if len(region) == 4:
            return BufferRegion(*region)

    def __str__(self):
        return json.dumps(self.pics, cls=MyEncoder, indent=4)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MatchPic):
            return obj.__str__()
        else:
            return super(MyEncoder, self).default(obj)


if __name__ == '__main__':
    br = BufferRegion(1, 2, 3, 4)
    brr = BufferRegionRect(10, 20)

    print(br)
    print(brr)
    if isinstance(br, BufferRegion):
        print("br is BufferRegion")
    if isinstance(br, BufferRegionRect):
        print("br is BufferRegionRect")
    if isinstance(brr, BufferRegion):
        print("brr is BufferRegion")
    if isinstance(brr, BufferRegionRect):
        print("brr is BufferRegionRect")

    # fp_soul = r'C:\Users\lijianye\Code\Nightingale\src\config\soul.yaml'
    # with open(fp_soul, 'r') as file:
    #     content = yaml.safe_load(file)
    #     print(json.dumps(content, indent=4))
    #     parser = MPParser(**content.get("soul").get("soul_invitees"))
    #     print(parser)

    fp_arknights = r'C:\Users\lijianye\Code\Nightingale\src\config\arknights.yaml'
    with open(fp_arknights, 'r') as file:
        content = yaml.safe_load(file)
        print(json.dumps(content, indent=4))
        parser = MPParser(**content.get("arknights").get("daily"))
        print(parser)
