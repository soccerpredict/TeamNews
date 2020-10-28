#!/usr/bin/python3
# -*- coding: utf-8 -*-
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from event_listenner import Listenner
from selenium.webdriver.support.events import EventFiringWebDriver
from selenium.webdriver.support import expected_conditions as EC
import urllib3
import os
import csv
import pathlib
from exceptions.path_exception import PathException
import json
import numpy as np
import time


class NewsCrawler(object):
    def __init__(self, date='', links=None, team=''):
        super(NewsCrawler, self).__init__()
        tester_conection = urllib3.PoolManager()
        print(":>> Verifying connection:", end='')
        
        #test your connection with the internet
        try:
            request = tester_conection.request(
                url="https://www.google.com", method="GET")
            if request.status == 200:
                print(" Successful connection. ")
        except urllib3.exceptions.MaxRetryError:
            print(" Unsuccessful connection.")
            del tester_conection
            return
        del tester_conection

        self.team = team
        opt = Options()
        opt.add_argument('--start-maximized')
        """
            By default, we start the page maximized.
            This feature prevent some bugs on the process of build data from comments.
        """
        self.driver: EventFiringWebDriver = EventFiringWebDriver(
            webdriver.Chrome(options=opt), Listenner(verbose=True))
            #we can add more features on the listenner, future jobs
            
        self.links = links
        self.date = date
        self.counter = 0

    def __exists_path(self, pathname) -> bool:
        if pathname[0] != '.':
            return pathlib.Path('./' + pathname).exists()
        return pathlib.Path(pathname).exists()

    def _get_files(self, pathname) -> list:
        if self.__exists_path(pathname):
            return list(pathlib.Path(pathname).glob('*.csv'))
        else:
            raise PathException(self.__exists_path(pathname))

    def __get_links(self, pathname) -> list:
        paths = self._get_files(pathname)
        data = []
        for i in paths:
            with i.open('r') as csvf:
                reader = csv.reader(csvf, delimiter=',')
                data.append([x[0] for x in reader])
        return list(data)

    def page_has_loaded(self) -> bool:
        """
            This function verify the state of one page.
            It was made to avoid errors of bad loading of the pages

        Returns:
            bool: 
                true -> Loaded
                false -> unloaded
        """
        page_state = self.driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    def __clearSubComment(self, element) -> dict:
        """
            This function extract the info's of subcomments of a comment.

        Args:
            element (webdriver.Element):

        Returns:
            dict: comment
        """
        aux = {}
        aux['name'] = element.find_element_by_tag_name("strong").text
        aux['text'] = element.find_element_by_tag_name("p").text
        aux['date'] = element.find_element_by_tag_name(
            "abbr").get_attribute("title")
        aux['likes'] = element.find_elements_by_tag_name("button")[1].text
        aux['unlikes'] = element.find_elements_by_tag_name("button")[2].text
        return aux

    def __clearComment(self, element) -> dict:
        """
            This function extract all the comments of one new

        Args:
            element (webdriver.Element):

        Returns:
            dict: comments
        """
        aux = {}
        aux['name'] = element.find_element_by_tag_name("strong").text
        aux['text'] = element.find_element_by_tag_name('p').text
        if aux['text'] == '':
            return

        aux['date'] = element.find_element_by_tag_name(
            "abbr").get_attribute("title")
        aux['likes'] = element.find_elements_by_tag_name("button")[1].text
        aux['unlikes'] = element.find_elements_by_tag_name("button")[2].text
        aux['replies'] = []

        replies = None
        n_replies = int(element.get_attribute("data-comentario-qtd_replies"))
        aux['n_replies'] = n_replies
        if n_replies > 0:
            replies = element.find_elements_by_tag_name("li")
            for i in replies:
                aux['replies'].append(self.__clearSubComment(i))

        return aux

    def __exec_load_button(self):
        """
            This function is responsible for click in all the buttons for expanse the comments
        """



        script = """
        bt = document.querySelectorAll('.glbComentarios-botao-mais');
        bt.forEach(b => {
           b.click(); 
        });
        bt = document.querySelectorAll('.glbComentarios-lista-bt-paginar');
        bt.forEach(b => {
           b.click(); 
        });
        """
        self.driver.execute_script(script)

    def build_page(self, link: str) -> bool:
        """this function is responsible for build the data from one page.

        Args:
            link ([str]): [url from the page]

        Returns:
            bool: [True-> success; False -> fail]
        """
        try:
            self.driver.get(link)
        except:
            print('Erro no link: <', link, '>')
            return False
        info = {}
        while not self.page_has_loaded():
            pass
        try:
            print("[LOG] Crawling data from new")
            info['time'] = str(self.driver.find_element(
                by=By.XPATH, value=".//a[contains(@class, 'header-editoria--link')]").text).lower()
            try:
                info['date'] = str(self.driver.find_element(
                    by=By.XPATH, value=".//time[contains(@itemprop, 'datePublished')]").text)
            except:
                info['date'] = 'no date'
            info['title'] = str(self.driver.find_element(
                by=By.XPATH, value="//h1[contains(@class, 'content-head__title')]").text) + '. ' + str(self.driver.find_element(by=By.XPATH, value="//h2[contains(@class, 'content-head__subtitle')]").text)
            info['author'] = str(self.driver.find_element(
                by=By.XPATH, value="//p[contains(@class, 'content-publication-data__from')]").get_attribute('title'))
            info['text'] = [i.text.replace('"', '').replace("'", '') for i in self.driver.find_elements(
                by=By.XPATH, value="//p[contains(@class, 'content-text__container')]")]
            element_aux = self.driver.find_element(
                by=By.XPATH, value="//div[contains(@class, 'entities')]")
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", element_aux)
            load_button = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
                (By.XPATH, "//button[contains(@class, 'glbComentarios-botao-mais')]")))
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", load_button)
            load_button.click()
            self.__exec_load_button()

            elements = self.driver.find_elements(
                by=By.XPATH, value="//ul[contains(@class, 'glbComentarios-lista-todos')]/li")
            info['comments'] = []
            print("[LOG] Crawling data from comments")
            for li in elements:
                comment = self.__clearComment(li)
                if comment != {} and comment != None:
                    info['comments'].append(comment)
            info['exception'] = 0
        except Exception as e:
            print("Exception ocurred on {}".format(self.counter), e)
            info['exception'] = 1
        info['url'] = link

        if info.get('time') != None:
            print('[LOG] Building file {!r}'.format(
                info['time'] + '_' + str(self.counter) + '.json'))
            with open('./news/' + info['time'] + '_' + str(self.counter) + '.json', 'w') as jsf:
                json.dump(info, jsf, indent=4, ensure_ascii=False)
                self.counter += 1
            print("Crawled {} news from {}.".format(
                self.counter, info['time']))
            return True
        else:
            return False

    def get_from_csv(self, pathname) -> None:
        """This function is responsible for checking all files that have already been downloaded and remove of the list of links

        Args:
            pathname ([type]): [path of the files]
        """
        links = {}
        for team in self.__get_links(pathname):
            for i in team:
                links[i] = 1

        existent_links = {}
        existent_path = list(pathlib.Path('./news').glob('*'))
        print('Consultando notícias já existentes ...')
        if len(existent_path) > 1:
            for i in existent_path:
                data = json.load(i.open())
                existent_links[data['url']] = 1
            self.counter = len(existent_links) + 1
            for k, v in existent_links.items():
                if links.get(k) != None:
                    links.pop(k)
        print(len(existent_links), 'notícias já baixadas, faltam ', len(links))
        [self.build_page(k) for k in list(links.keys())]


cr = NewsCrawler()
cr.get_from_csv('full_links')
