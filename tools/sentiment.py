import pandas as pd
import numpy as np

class SentimentPredictor(object):
    def __init__(self):
        # print('[LOG] Loadind DataFrame')
        self.news = pd.read_pickle('news.pkl')
        self.matches = pd.read_pickle('data.pkl')

    def favg_round(self, team: str, _round: int) -> float:
        df = self.news.query("team == '{}' and round == {}".format(team, _round))
        # avg = np.array([np.array(df.loc[k].compound_phrases).mean() for k in df.index])
        avg = []
        counter = 0
        for k in df.index:
            if np.array(df.loc[k].compound_phrases).size > 0:
                avg.append(np.array(df.loc[k].compound_phrases).mean())
                counter += 1
        if counter > 0:
            return np.array(avg).mean()
        else:
            return 0.0
        # print(df)
        # print("Avg vector: ", avg, avg.mean())
        # return avg.mean()

    def distance(self, avg_h: float, avg_v: float, rate: float) -> tuple:
        d = abs(max([avg_h, avg_v])) - abs(min([avg_h, avg_v]))

        if d <= rate:
            return (d, 'draw')
        else:
            if abs(avg_h) > abs(avg_v):
                return (d, 'home')
            else:
                return (d, 'visiting')

    def who_win(self, df):
        if df.goals_h > df.goals_v:
            return 'home'
        elif df.goals_v > df.goals_h:
            return  'visiting'
        else:
            return 'draw'


    def by_round(self, rate: float):
        counter_pred = 0
        counter_matches = 0
        for _round in range(2, 38):
            df = self.matches.query("round == {}".format(_round))
            for k in df.index:
                d = self.distance(self.favg_round(df.loc[k].team_id_home, _round), self.favg_round(df.loc[k].team_id_visiting, _round), rate)
                # print(df.loc[k])
                # print("Real winner: ", self.who_win(df.loc[k]))
                # print("Prediction: ", d)

                if self.who_win(df.loc[k]) == d[1]:
                    counter_pred += 1
                counter_matches += 1
                # input()
        # print("Final avg: ", (counter_pred/counter_matches)*100, " Rate: ", rate)
        print("rate: {} | score: {}".format(rate, (counter_pred/counter_matches)*100))
# pr = SentimentPredictor()

# rate = .01
# while True:
#     pr.by_round(rate)
#     rate += .01




