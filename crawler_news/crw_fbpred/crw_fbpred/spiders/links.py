# -*- coding: utf-8 -*-
import scrapy
import hashlib


class LinksSpider(scrapy.Spider):
	name = 'links'
	time = 'flamengo' # -a time='time'
	start_urls = [
		'https://globoesporte.globo.com/futebol/times/flamengo/index/feed/pagina-250.ghtml']
	links = []
	counter = 250
	file = 'links_{}.csv'.format(time)
	links_available = []
	first_time = True
	base_link = 'https://globoesporte.globo.com/futebol/times/%s' % time

	def populate(self):
		try:
			purelinks = open(self.file, 'r').read().split(',')
		except:
			return
		for link in purelinks:
			if link not in self.links_available:
				self.links_available.append(hashlib.sha1(bytes(link, 'utf-8')).hexdigest())

	def parse(self, response):

		if self.first_time:
			self.populate()
			self.first_time = False			
		dlinks = response.xpath('.//a[contains(@class, "feed-post-link")]/@href').extract()
		for l in dlinks:
			self.links.append(l)
		self.counter+=1
		# print(" >>> Counter:", self.counter)
		if self.counter % 10 == 0:
			fl = open(self.file, 'a+')
			for link in self.links:
				if (hashlib.sha1(bytes(link, 'utf-8')).hexdigest() not in self.links_available) and (self.base_link in link):
					# print(">>>",link, "\n>>>", self.base_link)
					fl.write(link + ',')
					self.links_available.append(hashlib.sha1(bytes(link, 'utf-8')).hexdigest())
			self.links.clear()
			fl.close()
		yield scrapy.Request(
			url='https://globoesporte.globo.com/futebol/times/flamengo/index/feed/pagina-%i.ghtml' % self.counter,
			callback=self.parse
		)