#!/usr/bin/python3
# -*- coding:utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import csv
import json

class GetStatistics(object):
    def __init__(self, path):
        self.path = path
        self.opt = Options()
        self.opt.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.opt)
        os.system('mkdir -p Statistics')
        # os.chdir('Statistics')
        self.links = []

    def get_data(self):
        with open (self.path) as file:
            reader = csv.reader(file)
            for row in reader:
                self.links.append(row[0])
            # print(self.links[0])
            #links adicionados
            os.chdir('Statistics')
            for i in self.links:
                try:
                    self.driver.get(i)
                    aux = self.driver.find_element_by_id('game-stats').text
                    self.cleaner(aux, i.split('/')[-2])
                    print(">>> Status 200")
                except Exception:
                    print(" >> 404: Error on link ", i)

    def cleaner(self, data, path):
        path = path.replace('-', '_')

        aux = data.split('\n')
        aux.pop(0)
        js = {}

        js['finalizations_mandant'] = int(aux[0].split(' ')[0])
        js['finalizations_visitant'] = int(aux[0].split(' ')[-1])
        js['kick_goal_mandant'] = int(aux[1].split(' ')[0])
        js['kick_goal_visitant'] = int(aux[1].split(' ')[-1])
        js['fault_mandant'] = int(aux[2].split(' ')[0])
        js['fault_visitant'] = int(aux[2].split(' ')[-1])
        js['impediment_mandant'] = int(aux[3].split(' ')[0])
        js['impediment_visitant'] = int(aux[3].split(' ')[-1])
        js['ownerb_mandant'] = int(aux[4].split(' ')[0])
        js['ownerb_visitant'] = int(aux[4].split(' ')[-1])
        js['corner_mandant'] = int(aux[5].split(' ')[0])
        js['corner_visitant'] = int(aux[5].split(' ')[-1])
        js['cross_mandant'] = int(aux[6].split(' ')[0])
        js['cross_visitant'] = int(aux[6].split(' ')[-1])
        js['yellowc_mandant'] = int(aux[7].split(' ')[0])
        js['yellowc_visitant'] = int(aux[7].split(' ')[-1])
        js['redc_mandant'] = int(aux[8].split(' ')[0])
        js['redc_visitant'] = int(aux[8].split(' ')[-1])
        self.writer(js, path)

    def writer(self, data, path):
        with open(path+'.json', 'w') as jsf:
            json.dump(data, jsf)


gt = GetStatistics('links_gen.csv')
gt.get_data()

