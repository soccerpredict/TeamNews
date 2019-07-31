#!/usr/bin/python3
#-*- encoding:utf-8 -*-
import json
import pathlib


class JsonCorrect(object):
    def __init__(self):
        self.path = ''
        self.files = []
        self.dump = json.dump
        self.data = {}
        self.teams = json.load(open('teams.json'))
    
    def populate(self, path):
        self.path = path
        self.files = list(pathlib.Path('.').glob(self.path + '/*.json'))
    
    def union_matches(self):
        for i in self.files:
            js = json.load(i.open())
            id = js.pop('id')
            for i in self.teams.keys():
                if js['id_winner'] == int(i):
                    js['id_winner'] = self.teams[i]
                if js['id_home_team'] == int(i):
                    js['id_home_team'] = self.teams[i]
                if js['id_visiting_team'] == int(i):
                    js['id_visiting_team'] = self.teams[i]
            self.data[id] = js
        return self.data
    
    def union_statistics(self):
        for i in self.files:
            js = json.load(i.open())
            id = js.pop('id')
            for i in self.teams.keys():
                if js['team_id'] == int(i):
                    js['team_id'] = self.teams[i]
            self.data[id] = js
        return self.data
    
    def union_news(self):      
        for i in self.files:
            js = json.load(i.open())
            id = js.pop('id')
            for i in self.teams.keys():
                if js['team_id'] == int(i):
                    js['team_id'] = self.teams[i]
            self.data[id] = js
        return self.data
    
    def clear(self):
        self.files.clear()
        self.data.clear()
        self.path = ''
        
    def write(self, path):
        with open(path, 'w') as jsf:
            self.dump(self.data, jsf, indent=4, ensure_ascii=False)
            
js = JsonCorrect()
js.populate('matches')
js.union_matches()
js.write('matches.json')
js.clear()

js.populate('statistics')
js.union_statistics()
js.write('statistics.json')
js.clear()

js.populate('news')
js.union_news()
js.write('news.json')
js.clear()
