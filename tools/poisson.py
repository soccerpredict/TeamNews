import pandas as pd
# import topandas
import numpy as np
import json
import sentiment

class Poisson():
    def __init__(self):
        self.df = pd.read_pickle('data.pkl')
        self.e = np.e

    def fact(self, x: int) -> int:
        if x == 0:
            return 1
        else:
            return x * self.fact(x - 1)

    def lambda_(self, team_h: str, team_v: str, round: int) -> tuple:
        
        lamb_x = 0
        lamb_y = 0
        # round = round - 1

        #Calculating lambda x
        """
            λx = team_h.goals_h.mean() + tean_v.goals_h.mean()
        """
        v1 = self.df.query("round <= {} and team_id_home == '{}'".format(round, team_h)).goals_h.mean()

        v2 = self.df.query("round <= {} and team_id_visiting == '{}'".format(round, team_v)).goals_h.mean()


        # print("\n\nID HOME ROUND <= ", round, "v1: ", v1)
        # print(self.df.query("round <= {} and team_id_home == '{}'".format(round, team_h)))

        # print("\n\nID VISITING ROUND <= ", round, "v2: ", v2)
        # print(self.df.query("round <= {} and team_id_visiting == '{}'".format(round, team_v)))

        lamb_x = (v1 + v2) / 2
        # print("Média de Gols da equipe mandante dentro de casa: ", v1, "\nMédia de Gols sofridos pela equipe visitante jogando fora de casa", v2, "\nMean:", lamb_x)

        # print()
        #Calculanting lambda y
        """
            λy = team_v.goals_v.mean()
        """
        v1 = self.df.query("round <= {} and team_id_visiting == '{}'".format(round, team_v)).goals_v.mean()
        v2 = self.df.query("round <= {} and team_id_home == '{}'".format(round, team_h)).goals_h.mean()
        lamb_y = (v1 + v2) / 2
        # print("Média de Gols da equipe visitante fora de casa: ", v1, "\nMédia de Gols sofridos pela equipe mandante jogando dentro de casa", v2, "\nMean:", lamb_y)
        # print("Output: ", (lamb_x, lamb_y))
        return (lamb_x, lamb_y)

    def poisson(self, x:int, y: int, mandant: str, visitant: str, round: int) -> float:
        lamb = self.lambda_(mandant, visitant, round)
        value = ((self.e**(-lamb[0])) * (self.e**(-lamb[1])) * (lamb[0]**x) * (lamb[1]**y)) / (self.fact(x) * self.fact(y))
        return value
    
    def build_values_from_matrix(self, matrix):
        win_prob = []
        draw_prob = []
        lose_prob = []
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i > j:
                    win_prob.append(matrix[i][j])
                elif i < j:
                    lose_prob.append(matrix[i][j])
                else:
                    draw_prob.append(matrix[i][j])
        return (sum(win_prob), sum(draw_prob), sum(lose_prob))

    def poisson_percent(self, x:int, y: int, mandant: str, visitant: str, round: int, comp_mandant: float, comp_visitant: float) -> float:
        lamb = self.lambda_(mandant, visitant, round)
        lamb = ((lamb[0] + (comp_mandant*lamb[0])), (lamb[1] + (comp_mandant*lamb[1])))
        value = ((self.e**(-lamb[0])) * (self.e**(-lamb[1])) * (lamb[0]**x) * (lamb[1]**y)) / (self.fact(x) * self.fact(y))
        return value

    def by_round_with_sentiment(self):
        full_acc = []
        sent = sentiment.SentimentPredictor()
        for i in range(2, 38):
            df = self.df.query('round == {}'.format(i))
            match_counter = 0
            round_acc = 0
            round_d = {}

            for k in df.index:

                aux = {}
                pois_predict = []
                for goals_m in range(6):
                    aux_pois = []
                    for goals_v in range(6):
                        aux_pois.append(self.poisson_percent(goals_m, goals_v, df.loc[k].team_id_home, df.loc[k].team_id_visiting, i, sent.favg_round(df.loc[k].team_id_home, i), sent.favg_round(df.loc[k].team_id_visiting, i))*100)
                    pois_predict.append(aux_pois)

                # print("Mandant: ", df.loc[k].team_id_home)
                # print("Visitant: ", df.loc[k].team_id_visiting)
                # print("Round: ", i)
                # print("Placar real: ", (df.loc[k].goals_h, df.loc[k].goals_v))
                # print("Predictions: ", self.build_values_from_matrix(pois_predict))
                # for l in pois_predict:
                #     print(l)
                # soma = 0
                # for j in pois_predict:
                #     soma += sum(j)
                # print("Soma: ", soma)
                aux['mandant'] = df.loc[k].team_id_home
                aux['visitant'] = df.loc[k].team_id_visiting
                aux['score'] = (df.loc[k].goals_h, df.loc[k].goals_v)
                aux['date'] = df.loc[k].date
                aux['prob_matrix'] = pois_predict
                aux['predictions'] = self.build_values_from_matrix(pois_predict)
                aux['percent_mandant'] = sent.favg_round(df.loc[k].team_id_home, i)
                aux['percent_visitant'] = sent.favg_round(df.loc[k].team_id_visiting, i)

                if df.loc[k].goals_h > df.loc[k].goals_v:
                    aux['winner'] = 'mandant'
                elif df.loc[k].goals_h < df.loc[k].goals_v:
                    aux['winner'] = 'visitant'
                else:
                    aux['winner'] = 'draw'
                
                if max(aux['predictions']) == aux['predictions'][0]:
                    aux['prob_winner'] = 'mandant'
                elif max(aux['predictions']) == aux['predictions'][1]:
                    aux['prob_winner'] = 'draw'
                else:
                    aux['prob_winner'] = 'visitant'
                
                if aux['winner'] == aux['prob_winner']:
                    round_acc += 1
                    aux['result'] = '1'
                else:
                    aux['result'] = '0'
                round_d[str(match_counter)] = aux
                match_counter += 1                    
            with open('rounds_sentiment/round_{}.json'.format(i), 'w') as jsf:
                json.dump(round_d, jsf, ensure_ascii=False, indent=2)
            print("Round: {} | Acc: {} | Matches: {}".format(i, round_acc/len(df), len(df)))
            full_acc.append(round_acc/len(df))
        print("Acurácia final: ", np.array(full_acc).mean())
        print(full_acc)



    def by_round(self):
        full_acc = []
        draw = 0
        for i in range(2, 38):
            df = self.df.query('round == {}'.format(i))
            match_counter = 0
            round_acc = 0
            round_d = {}

            for k in df.index:

                aux = {}
                pois_predict = []
                for goals_m in range(6):
                    aux_pois = []
                    for goals_v in range(6):
                        aux_pois.append(self.poisson(goals_m, goals_v, df.loc[k].team_id_home, df.loc[k].team_id_visiting, i)*100)
                    pois_predict.append(aux_pois)

                # print("Mandant: ", df.loc[k].team_id_home)
                # print("Visitant: ", df.loc[k].team_id_visiting)
                # print("Round: ", i)
                # print("Placar real: ", (df.loc[k].goals_h, df.loc[k].goals_v))
                # print("Predictions: ", self.build_values_from_matrix(pois_predict))
                # for l in pois_predict:
                #     print(l)
                # soma = 0
                # for j in pois_predict:
                #     soma += sum(j)
                # print("Soma: ", soma)
                aux['mandant'] = df.loc[k].team_id_home
                aux['visitant'] = df.loc[k].team_id_visiting
                aux['score'] = (df.loc[k].goals_h, df.loc[k].goals_v)
                aux['date'] = df.loc[k].date
                aux['prob_matrix'] = pois_predict
                aux['predictions'] = self.build_values_from_matrix(pois_predict)

                if df.loc[k].goals_h > df.loc[k].goals_v:
                    aux['winner'] = 'mandant'
                elif df.loc[k].goals_h < df.loc[k].goals_v:
                    aux['winner'] = 'visitant'
                else:
                    aux['winner'] = 'draw'
                    draw += 1
                
                if max(aux['predictions']) == aux['predictions'][0]:
                    aux['prob_winner'] = 'mandant'
                elif max(aux['predictions']) == aux['predictions'][1]:
                    aux['prob_winner'] = 'draw'
                else:
                    aux['prob_winner'] = 'visitant'
                
                if aux['winner'] == aux['prob_winner']:
                    round_acc += 1
                    aux['result'] = '1'
                else:
                    aux['result'] = '0'
                round_d[str(match_counter)] = aux
                match_counter += 1                    
            with open('rounds/round_{}.json'.format(i), 'w') as jsf:
                json.dump(round_d, jsf, ensure_ascii=False, indent=2)
            print("Round: {} | Acc: {} | Matches: {}".format(i, round_acc/len(df), len(df)))
            full_acc.append(round_acc/len(df))
        print("Acurácia final: ", np.array(full_acc).mean())
        print(full_acc)
        print("Draws: ", draw)


    def build_results(self):        
        result = {}
        data_frame = self.df.query("round > 2")
        counter = 0
        miss_counter = 0
        hit_counter = 0
        for i in data_frame.index:
            aux = {}
            aux['mandant'] = self.df.loc[i].team_id_home
            aux['visitant'] = self.df.loc[i].team_id_visiting
            if self.df.loc[i].goals_h > self.df.loc[i].goals_v:
                aux['winner'] = 'mandant'
            elif self.df.loc[i].goals_h < self.df.loc[i].goals_v:
                aux['winner'] = 'visitant'
            else:
                aux['winner'] = 'draw'
            aux['score'] = (self.df.loc[i].goals_h, self.df.loc[i].goals_v)
            aux['round'] = str(self.df.loc[i]['round'])
            aux['date'] = self.df.loc[i].date

            scores = []
            for i in range(6):
                sc = []
                for j in range(6):
                    sc.append(self.poisson(i,j, aux['mandant'], aux['visitant'], int(aux['round'])))
                scores.append(sc)
            aux['predictions'] = scores
            win_prob = []
            draw_prob = []
            lose_prob = []
            for i in range(len(aux['predictions'])):
                for j in range(len(aux['predictions'])):
                    # print(i, j)
                    if i > j:
                        # print("Win prob")
                        win_prob.append(aux['predictions'][i][j])
                    elif i < j:
                        # print("Lose prob")
                        lose_prob.append(aux['predictions'][i][j])
                    else:
                        # print("Draw prob")
                        draw_prob.append(aux['predictions'][i][j])
                    # input()
            aux['win_prob'] = str(np.array(win_prob).sum())
            aux['draw_prob'] = str(np.array(draw_prob).sum())
            aux['lose_prob'] = str(np.array(lose_prob).sum())

            real = ''
            if aux['score'][0] > aux['score'][1]:
                real = 'win'
            elif aux['score'][0] < aux['score'][1]:
                real = 'lose'
            else:
                real = 'draw'
            
            predicted = ''
            if max([aux['win_prob'], aux['draw_prob'], aux['lose_prob']]) == aux['win_prob']:
                predicted = 'win'
            elif max([aux['win_prob'], aux['draw_prob'], aux['lose_prob']]) == aux['draw_prob']:
                predicted = 'draw'
            elif max([aux['win_prob'], aux['draw_prob'], aux['lose_prob']]) == aux['lose_prob']:
                predicted = 'lose'
            # print(aux['win_prob'], aux['draw_prob'], aux['lose_prob'], predicted)
            if predicted == real:
                aux['result'] = 'hit'
                hit_counter += 1
            else:
                aux['result'] = 'miss'
                miss_counter += 1
            result[str(counter)] = aux
            counter += 1
            print("Builded {} matches for round {}".format(counter, aux['round']))
            if aux['mandant'] == 'fluminense' and aux['visitant'] == 'flamengo' and aux['round'] == 10:
                print(aux)
        print("Hits: ", hit_counter)
        print("Miss: ", miss_counter)
        print("Score: ", hit_counter / 360)
        with open('results.json', 'w') as jsf:
            json.dump(result, jsf, ensure_ascii=False, indent=2)
            # print(aux['predictions'], '\n')
            # print("Win: ", aux['win_prob'])
            # print("Draw: ", aux['draw_prob'])
            # print("Lose: ", aux['lose_prob'], '\n')

            # print('Win prob: ', np.array(win_prob).mean()*100)
            # print('Draw prob: ', np.array(draw_prob).mean()*100)
            # print('Lose prob: ', np.array(lose_prob).mean()*100)
            # print('Real score: ', aux['score'])

            # input()
            # input()



# p = Poisson()
# p.by_round_with_sentiment()



# p.build_results()

# p.by_round_with_sentiment()
# data = []
# for i in range(6):
#     aux = []
#     for j in range(6):
#         aux.append(p.poisson(i,j))
#         print("Placar: [{}, {}] : Prob: {}".format(i,j,p.poisson(i,j)))
#     data.append(aux)

# data_frame = pd.DataFrame(columns=['0','1','2','3','4','5'])
# for i in range(len(data)):
#     print(data[i])
#     data_frame.loc[i] = data[i]

# data_frame.to_pickle('table.pkl')





# TODO:


""" compound médio de cada rodada
    distancia = valor absoluto de mandante - abs visitante
    limiar = .05

    limiar < .05 => + pra empate
    maior valor => maior probabilidade para vitória do maior valor de compound
    analisar limiar por rodada
"""