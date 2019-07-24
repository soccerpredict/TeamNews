# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

class CrwFbpredPipeline(object):

    def stringer(self, dados):
        sstring = ''
        for i in dados:
            sstring += i
        return sstring

    def process_item(self, item, spider):
        
        item['text'] = self.stringer(item['text'])
        # spider.log('--- Capturado ---')

        with open(str(item['time'] + '_' + str(item['id']))+'.json', 'w') as jsf:
            json.dump(item, jsf)

        # return item
