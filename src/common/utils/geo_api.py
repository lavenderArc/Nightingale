#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2022-2022, Inc. All Rights Reserved 
#
# Function: GeoUtils
import random


class GeoUtils:
    @staticmethod
    def box_center(b):
        """
        get box center position
        :param b: Box(left, top, width, height)
        :return: position
        """
        if b:
            return b.left + b.width // 2, b.top + b.height // 2
        return 0, 0

    @staticmethod
    def size_center(sz):
        """
        get size center
        :param sz: (width, height)
        :return: position
        """
        if sz:
            return sz.width // 2, sz.height // 2
        return 0, 0

    @staticmethod
    def random_position(pos, buffer):
        """
        get random position with random buffer.
        :param pos: exact position
        :param buffer: random buffer
        :return: random position, random value
        """
        width_random, height_random = random.randint(-buffer[0], buffer[0]), random.randint(-buffer[1], buffer[1])
        return (pos[0] + width_random, pos[1] + height_random), (width_random, height_random)
