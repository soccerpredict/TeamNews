#!/usr/bin/python3
# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import pathlib
import json
import sys
import unicodedata

def build(k:str) -> str:
	if k != '':
		if k.startswith(' '):
			k = k.replace(' ', '', 1)
		k = k.replace('+ ', ' ').replace('- ', ' ').replace(' ,', ', ').replace('\n', ' ')
		ucod = unicodedata.normalize("NFKD", k)
		k = u"".join([c for c in ucod if not unicodedata.combining(c)])
		return k + '.'
	return ''

def dot_spliter(data: dict) -> None:
	phrases = list()
	if data.get('text') != None:
		for i in data['text']:
			for k in i.split('.'):
				phrases.append(build(k))
		data['phrases'] = phrases

	if data.get('comments') != None:
		comments = []
		for i in data['comments']:
			for k in i['text'].split('.'):
				comments.append(build(k))
			if i['n_replies'] > 0:
				for j in i['replies']:
					for k in j['text'].split('.'):
						comments.append(build(k))
		data['comments_phrases'] = comments

	

def dot_spliter_runner(data: list) -> None:
	print("[LOG] Building data from json files")
	with ThreadPoolExecutor() as exec:
		exec.map(dot_spliter, data)

def dot_spliter_run() -> list:
	"""
		This function build a list with all news with two more fields:
			'phrases' -> is a list with all phrases separated by a dot, from the text of the new
			'comments_phrases' -> is a list with all phrases separeted by a dot, from the comments of the new

	Returns:
		list: [dict, dict ...]
		keys:
			time
			date
			text
			author
			title
			comments
			exception
			url
			phrases
			comments_phrases
	"""

	if sys.path[0].endswith('preprocess'):
		p = list(pathlib.Path('../data/news').glob('*/*.json'))
	else:
		p = list(pathlib.Path(sys.path[0] + '/news').glob('*.json'))
	data = []
	print("[LOG] Reading JSON files")
	for i in p:
		aux = json.load(i.open())
		if aux.get('text') != None and aux['exception'] == 0:
			data.append(aux)
	dot_spliter_runner(data)
	print("[LOG] Cleaning empty phrases")
	for i in data:
		if i.get('phrases') != None and i.get('comments_phrases') != None:
			i['phrases'] = [k for k in i['phrases'] if k != '']
			i['comments_phrases']= [k for k in i['comments_phrases'] if k != '']
	print("[LOG] Process successfully build")
	return data

