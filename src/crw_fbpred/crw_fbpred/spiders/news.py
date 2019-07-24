# -*- coding: utf-8 -*-
import scrapy
import os
import json
import time
from datetime import datetime

class NewsSpider(scrapy.Spider):
    name = 'news'
    start_urls = ['https://globoesporte.globo.com/futebol/times/cruzeiro/noticia/cruzeiro-encerra-brasileirao-e-tenta-acumular-r-75-milhoes-em-premiacoes-no-ano.ghtml']
    counter = 1
    path_file = ''
    urls = []
    first_time = True
    date_begin = '07/04/2018'
    date_end = '02/12/2018'
# [ 'santos']
    def populate(self):
        self.urls = open('links_vitoria.csv', 'r').read().split(',')
        os.system('mkdir -p Dados')
        os.chdir("Dados")
        os.system("mkdir -p vitoria")
        os.chdir("vitoria")
        # with open(self.path_file, 'r') as fl:
        #     reader = csv.reader(fl, delimiter=',')
        #     for lin in reader:
        #         self.urls.append(lin)
    
    def date_correction(self, date):

        if date != None:
            real_date = time.mktime(datetime.strptime(str(date), '%d/%m/%Y' ).timetuple())
            date_1 = time.mktime(datetime.strptime(str(self.date_begin), '%d/%m/%Y' ).timetuple())
            date_2 = time.mktime(datetime.strptime(str(self.date_end), '%d/%m/%Y' ).timetuple())
            print(">>>> ", date_1 <= real_date <= date_2)
            return date_1 <= real_date <= date_2
        return False

    def parse(self, response):
        flag = True
        if self.first_time:
            self.populate()
            self.first_time = False
            self.start_urls[0] = self.urls[0]


        date = response.xpath('.//time[contains(@itemprop, "datePublished")]/text()').extract_first()
        if date != None and date != []:
            date = date.split(" ")[1]
        
        if not self.date_correction(date):
            flag = False

        time = response.xpath('.//a[contains(@class, "header-editoria--link")]/text()').extract_first().encode().decode('utf-8')
        
        title = response.xpath('//div[contains(@class, "title")]/meta/@content').extract()
        title = [p.encode().decode('utf-8') for p in title]
        
        author = response.xpath('//p[contains(@class, "content-publication-data__from")]/@title').extract()
        author = [p.encode().decode('utf-8') for p in author]
        
        text = response.xpath('//p[contains(@class, "content-text__container")]/text()').extract()
        text = [p.encode().decode('utf-8') for p in text]
        
        if flag:
            yield{
                'time': time,
                'title': title,
                'author': author,
                'text': text,
                'date': date,
                'url': response.url,
                'id': self.counter
            }
            self.counter += 1
            yield scrapy.Request(
                url=str(self.urls.pop(0)),
                callback=self.parse
            )
        else:
            yield scrapy.Request(
                url=str(self.urls.pop(0)),
                callback=self.parse
            )
        
