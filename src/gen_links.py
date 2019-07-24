
import csv
import requests

class Gen(object):
    def __init__(self, path, delimiter):
        self.campos = list()
        self.database = list()
        self.dados = dict()
        self.delimiter = delimiter
        self.path = path
        self.links = []

    def gen(self):
        with open(self.path, 'r') as csvf:
            reader = csv.reader(csvf, delimiter=self.delimiter)
            first = True
            campos = []
            for row in reader:
                if first:
                    for i in row:
                        campos.append(i.lower())
                    first = False
                else:
                    for i in range(len(campos)):
                        self.dados[campos[i]] = row[i]
                    self.database.append(self.dados.copy())
                    # self.dados.clear()
    def populate(self):
        for i in self.database:
            mandante = i['time_mandante']
            visitante = i['time_visitante']
            data = i['data']

            aux = data.split('/')[0]
            aux += data.split('/')[1]
            aux += '2018'
            data = aux

            link = 'https://veja.abril.com.br/placar/campeonato-brasileiro/{}-e-{}-{}/'.format(mandante, visitante, data)
            req = requests.get(link)
            if(req.status_code == 200):
                print(">>> Request status:", req.status_code)
                self.links.append(link)
            else:
                print(">>> Request status:", req.status_code, link)
            req.close()
            del req
    def write(self):
        with open('links_gen.csv', 'a+') as csvf:
            spam = csv.writer(csvf, delimiter=self.delimiter)
            for i in self.links:
                spam.writerow([i])

gen = Gen('tab_jogos_2018.csv', ';')
gen.gen()
gen.populate()
gen.write()