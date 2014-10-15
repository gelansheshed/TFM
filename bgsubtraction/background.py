#!/usr/bin/env python

from bgsubtraction import cbackground
from bgsubtraction import cv2
from bgsubtraction import np


class Bg(object):

    """
    Parent class of the Background class that contains common
    attributes shared by every Background object
    """

    def __init__(self):

        self.option = None
        self.alpha = None
        self.beta = None
        self.frame_count = None
        self.threshold_1 = None
        self.threshold_2 = None

    def setdefault(self):

        self.option = 0
        self.alpha = 0.9
        self.beta = 0.1
        self.frame_count = 30
        self.threshold_1 = 25
        self.threshold_2 = 5


class Background(object):

    """
    Background class contains the different parameters and
    attributes the application background model needs.This
    object is intended to be adaptable for each camera view.
    """

    def __init__(self, bg):

        self.bg = bg
        self.counter = None
        self.win_height = None
        self.win_width = None
        self.win_min_pix = None
        self.bg_img = None
        self.bin_img = None
        self.bin_img_2 = None
        self.scan_img = None
        self.diff_img = None
        self.contours = None

    def setdefault(self, src):

        size = src.shape
        height = size[0]
        width = size[1]

        self.counter = 1
        self.win_height = 30
        self.win_width = 15
        self.win_min_pix = 200
        self.bg_img = src
        self.bin_img_1 = np.zeros((height, width))
        self.bin_img_2 = self.bin_img
        self.scan_img = self.bin_img
        self.diff_img = self.bin_img
        self.contours = None

    def updatebackground(self, src):

        if self.bg_img.any():
            if self.bg.frame_count is self.counter:
                self.bg_img = cv2.addWeighted(
                    self.bg_img, self.bg.alpha, src, self.bg.beta, 0)
                self.counter = 1

            else:
                self.counter += 1

        else:
            raise Exception('Background model parameters not initialized \n '
                            'Please initiatilize parameters with '
                            'setdefault() function')

    def subtractbackground(self, src):

        if self.bg_img.any():
            subtract = cv2.subtract(self.bg_img, src)
            self.bin_img_1 = self._thresholdbackground(
                subtract, self.bg.threshold_1)
            self.bin_img_2 = self._thresholdbackground(
                subtract, self.bg.threshold_2)

        else:
            raise Exception('Background model parameters not initialized \n '
                            'Please initiatilize parameters with '
                            'setdefault() function')

    def _thresholdbackground(self, src, threshold):

        ret, threshold_0 = cv2.threshold(
            src[:, :, 0], threshold, 255, cv2.THRESH_BINARY)
        ret, threshold_1 = cv2.threshold(
            src[:, :, 1], threshold, 255, cv2.THRESH_BINARY)
        ret, threshold_2 = cv2.threshold(
            src[:, :, 2], threshold, 255, cv2.THRESH_BINARY)

        return cv2.add(threshold_0.astype(np.uint8), cv2.add(
            threshold_1.astype(np.uint8), threshold_2.astype(np.uint8)))

    def windowscanbackground(self):

        if self.bin_img_1.any():
            int_img = cv2.integral(self.bin_img_1)
            self.scan_img = cbackground.scanningwindow(
                int_img, self.win_height, self.win_width, self.win_min_pix)

        else:
            raise Exception('Background model images not updated \n '
                            'Please update model images with '
                            'subtractbackground() function')

    def thresholdbackground(self):

        if self.bin_img_1.any():
            self.diff_img = cv2.multiply(self.bin_img_2, self.scan_img)

        else:
            raise Exception('Background model images not updated \n '
                            'Please update model images with '
                            'subtractbackground() function')

    def contoursbackground(self):

        if self.bin_img_1.any():
            self.contours, hierarchy = cv2.findContours(
                self.diff_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        else:
            raise Exception('Background difference image not updated \n'
                            'Please update difference image with '
                            'thresholdbackground() function')
