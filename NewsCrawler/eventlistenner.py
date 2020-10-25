#!/usr/bin/python3
# -*- coding:utf-8 -*-

from selenium.webdriver.support.events import AbstractEventListener
from selenium import webdriver
import sys
import time


class Listenner(AbstractEventListener):
    def __init__(self, verbose=True):
        self.verbose = verbose

    def after_navigate_to(self, url, driver):
        if self.verbose:
            print("[LOG Listenner] Acessed", url)
            print('[LOG Listenner] Loading .', flush=True, end='')
            while driver.execute_script('return document.readyState;') != 'complete':
                print('.', end='', flush=True)
                time.sleep(.3)
            print()
        else:
            while driver.execute_script('return document.readyState;') != 'complete':
                time.sleep(.3)
    def after_click(self, url, driver):
        pass
