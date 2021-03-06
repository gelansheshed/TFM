#!/usr/bin/env python

"""
Initialization of the project global variables
"""

import cv2
import os

from var import variables


def init():

    initvariables()


def initvariables():

    variables.app_path = os.path.dirname(os.path.realpath(__file__))
    variables.datasets_path = variables.app_path + '/data'

    """
    variables.datasets_name = {
        1: 'grazptz1',
        2: 'grazptz2',
        3: 'pets091',
        4: 'pets092',
        5: 'pets093',
        6: 'pets094',
        7: 'pets095',
        8: 'pets096',
        9: 'pets097',
        10: 'pets098',
        11: 'pets099',
        12: 'oxtown'}
    """
    """
    variables.datasets_name = {
        1: 'caviar01',
        2: 'caviar02',
        3: 'caviar03',
        4: 'caviar04',
        5: 'caviar05'
    }
    """
    variables.datasets_name = {
        1: 'pets01_crop',
        2: 'pets091',
        3: 'ewap01',
        4: 'oxtown',
        5: 'grazptz1',
        6: 'pets094',
        7: 'pets095'
    }
    variables.app_window_name = 'Main Window'
    variables.app_window = cv2.namedWindow(
        variables.app_window_name, cv2.WINDOW_NORMAL)

    variables.app_window_trackbar_name = 'Main Background Window'
    variables.app_window_trackbar = cv2.namedWindow(
        variables.app_window_trackbar_name, cv2.WINDOW_NORMAL)

    variables.app_window_trackbar_name_2 = 'Secondary Background Window'
    variables.app_window_trackbar_2 = cv2.namedWindow(
        variables.app_window_trackbar_name_2, cv2.WINDOW_NORMAL)
