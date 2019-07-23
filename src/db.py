#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import json
import pathlib
import pandas
import os
import datetime

host = '127.0.0.1'
user = 'root'
password = ''
db = 'fbpred'
cnx = connection.MySQLConnection(
    user=user, password=password, host=host, database=db)
cursor = cnx.cursor()

def insert_teams(cnx, cursor):
    teams = ['sao-paulo', 'vasco', 'atletico-mg', 'ceara', 'corinthians', 'fluminense', 'parana-clube', 'palmeiras', 'sport', 'vitoria', 'bahia', 'botafogo', 'flamengo', 'cruzeiro', 'chapecoense', 'internacional', 'gremio', 'atletico-pr', 'america-mg', 'santos']
    # query = ("insert into fbpred.teams(id, team_name) values (%s, %s);")
    # data = ('default', 'atletico-mg')
    # cursor.execute(query, data)
    cont = 1
    for team in teams:
        query = ("insert into fbpred.teams(id, team_name) values (%s, %s);")
        data = (str(cont), str(team))
        cont += 1
        cursor.execute(query, data)
    cursor.execute("insert into fbpred.teams(id, team_name) values(default, 'empate');")
    cnx.commit()

def clean(teams):
    mandant = ''
    visitant = ''
    teams = teams.split('/')[1]
    l = teams.split('_')
    flag1 = False
    # print(l, len(l))
    if l[1] == 'e':
        mandant = l[0]
        flag1 = True
    else:
        mandant = l[0] + '-' + l[1]
    
    
    # print(l, len(l))
    if l[-2] == 'pr' or l[-2] == 'mg' or l[-2] == 'clube' or l[-2] == 'paulo':
        visitant = l[-3] + '-' + l[-2]
    else:
        visitant = l[-2]
    date = l[-1].split('.')[0]
    rdate = date[0] + date[1] + '/' + date[2] + date[3] + '/' + date[4] + date[5] + date[6] + date[7]
    return mandant, visitant, rdate
    

def find_game(df, data, mandant):
    count = 0
    for i in df.DATA:
        if str(i) == str(data):
            if df.TIME_MANDANTE.ix[count] == mandant:
                # print(">> Match find")
                return df.ix[count]
                
        count += 1

        
def insert_matchs_statistics(cnx, cursor):
    arquivos = sorted(pathlib.Path('.').glob('./Statistics/*.json'))
    arquivos = ['Statistics/' + p.name for p in arquivos]
    df = pandas.read_csv('tab_jogos_2018.csv', delimiter=';')
    
    os.system('mkdir -p matches')

    counter_match = 0
    statistic_counter = 0
    for i in arquivos:
        try:
            js = json.load(open(i))
            # print(clean(i))
            mandant, visitant, data = clean(i)
            
            # print(">>> ", mandant, visitant)
            match = {}
            frame = find_game(df, str(data), mandant)
            print(">", str(data), mandant, visitant)
            match['date'] = datetime.date(int(data.split('/')[2]), int(data.split('/')[1]), int(data.split('/')[0]))
            match['attendance'] = int(frame.PUBLICO)
            match['income'] = float(frame.RENDA.split(' ')[1].replace('.', '').replace(',', '.'))
            
            cursor.execute("select id from fbpred.teams where fbpred.teams.team_name = '{}'".format(mandant))
            id_mandant = cursor.fetchone()[0]
            
            cursor.execute("select id from fbpred.teams where fbpred.teams.team_name = '{}'".format(visitant))
            id_visitant = cursor.fetchone()[0]
            
            cursor.execute("select id from fbpred.teams where fbpred.teams.team_name = '{}'".format(frame.VENCEDOR))
            id_winner = cursor.fetchone()[0]
            
            match['id_winner'] = id_winner
            match['id_home_team'] = id_mandant
            match['id_visiting_team'] = id_visitant
            match['id'] = counter_match
            
            cursor.execute("insert into fbpred.matches(id, date, attendance, income, id_home_team, id_visiting_team, id_winner) values (%(id)s, %(date)s, %(attendance)s, %(income)s, %(id_home_team)s, %(id_visiting_team)s, %(id_winner)s);", match)
            
            match['date'] = data
            os.chdir('Matches')
            with open('match_' + str(counter_match) + '.json', 'w') as jsf:
                json.dump(dict(match), jsf)
            os.chdir('..')
            
            os.system('mkdir -p statistics')
            os.chdir('statistics')
            
            statistic_mandant = {}
            statistic_mandant['id'] = int(statistic_counter)
            statistic_mandant['team_id'] = int(id_mandant)
            statistic_mandant['match_id'] = int(match['id'])
            statistic_mandant['status'] = 'h'
            statistic_mandant['shots'] = int(js['finalizations_mandant'])
            statistic_mandant['shots_on_goal'] = int(js['kick_goal_mandant'])
            statistic_mandant['fouls'] = int(js['fault_mandant'])
            statistic_mandant['offsides'] = int(js['impediment_mandant'])
            statistic_mandant['ball_possession'] = int(js['ownerb_mandant'])
            statistic_mandant['corners'] = int(js['corner_mandant'])
            statistic_mandant['cross'] = int(js['cross_mandant'])
            statistic_mandant['yellow_cards'] = int(js['yellowc_mandant'])
            statistic_mandant['red_cards'] = int(js['redc_mandant'])
            statistic_mandant['goals'] = int(frame.PLACAR.split(',')[0])
            
            with open('statistics_' + str(statistic_counter) + '.json', 'w') as jsf:
                json.dump(statistic_mandant, jsf)
            statistic_counter += 1
                        
            statistic_visitant = {}
            statistic_visitant['id'] = statistic_counter
            statistic_visitant['team_id'] = id_visitant
            statistic_visitant['match_id'] = match['id']
            statistic_visitant['status'] = 'v'
            statistic_visitant['shots'] = js['finalizations_visitant']
            statistic_visitant['shots_on_goal'] = js['kick_goal_visitant']
            statistic_visitant['fouls'] = js['fault_visitant']
            statistic_visitant['offsides'] = js['impediment_visitant']
            statistic_visitant['ball_possession'] = js['ownerb_visitant']
            statistic_visitant['corners'] = js['corner_visitant']
            statistic_visitant['cross'] = js['cross_visitant']
            statistic_visitant['yellow_cards'] = js['yellowc_visitant']
            statistic_visitant['red_cards'] = js['redc_visitant']
            statistic_visitant['goals'] = frame.PLACAR.split(',')[1]
            
            with open('statistics_' + str(statistic_counter) + '.json', 'w') as jsf:
                json.dump(statistic_visitant, jsf)
            statistic_counter += 1
            
            query = "insert into fbpred.statistics(`id`, `team_id`, `match_id`, `status`, `shots`, `shots_on_goal`, `fouls`, `offsides`, `ball_possession`, `corners`, `cross`, `yellow_cards`, `red_cards`, `goals`) values (%(id)s, %(team_id)s, %(match_id)s, %(status)s, %(shots)s, %(shots_on_goal)s, %(fouls)s, %(offsides)s, %(ball_possession)s, %(corners)s, %(cross)s, %(yellow_cards)s, %(red_cards)s, %(goals)s);"
            cursor.execute(query, statistic_mandant)
            cursor.execute(query, statistic_visitant)
                      
            os.chdir('..')            
            counter_match += 1
        except json.decoder.JSONDecodeError as err:
            print(">>>", err, i)
    cnx.commit()
        

# insert_matchs_statistics(cnx, cursor)


# from pathlib import path
# dados = sorted(Path('.').glob('./Dados/*/*.json'))

# with open(dados[0], 'r') as f:
