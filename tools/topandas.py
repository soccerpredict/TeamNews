import pathlib
import pandas as pd
import json
import numpy as np
from cleaners import dot_spliter_run
import sys
from leia import SentimentIntensityAnalyzer


def populate_dataframe() -> pd.DataFrame:
    data_frame = pd.DataFrame(columns=['team',
                                       'date',
                                       'title',
                                       'author',
                                       'text',
                                       'comments',
                                       'url',
                                       'phrases',
                                       'comments_phrases',
                                       ])
    data = dot_spliter_run()
    print("[LOG] Building DataFrame from pandas")
    for i in range(len(data)):
        if data[i]['phrases'] != []:
            aux = [data[i]['team'].replace('é', 'e').replace('ó', 'o').replace('ã', 'a').replace('ê', 'e').replace('í', 'i').replace('-', '_').replace('á', 'a'), data[i]['date'], data[i]['title'], data[i]['author'], data[i]['text'],
                   data[i]['comments'], data[i]['url'], data[i]['phrases'], data[i]['comments_phrases']]
            data_frame.loc[i] = aux
    return data_frame


def populate_lexicon_analysis(df: pd.DataFrame) -> pd.DataFrame:
    phrases, comments = [], []
    analyser = SentimentIntensityAnalyzer()
    print('[LOG] Building analysis from phrases')
    comp_serie = []
    comp_comments = []
    for k in df.phrases:
        if len(k) > 0:
            aux = {'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0}
            aux_serie = []
            for j in k:
                an = analyser.polarity_scores(j)
                aux['neg'] += an['neg']
                aux['pos'] += an['pos']
                aux['neu'] += an['neu']
                aux['compound'] += an['compound']
                aux_serie.append(an['compound'])
            # print('Vanilla: ', aux, len(k))
            aux['neg'] /= len(k)
            aux['pos'] /= len(k)
            aux['neu'] /= len(k)
            aux['compound'] /= len(k)
            phrases.append(aux)
            comp_serie.append(aux_serie)
        else:
            phrases.append({'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0})
        # print('Processed: ', aux)
    print('[LOG] Building analysis from comments')
    for k in df.comments_phrases:
        if len(k) > 0:
            aux = {'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0}
            aux_serie = []
            for j in k:
                an = analyser.polarity_scores(j)
                aux['neg'] += an['neg']
                aux['pos'] += an['pos']
                aux['neu'] += an['neu']
                aux['compound'] += an['compound']
                aux_serie.append(an['compound'])
            # print('Vanilla: ', aux, len(k))
            aux['neg'] /= len(k)
            aux['pos'] /= len(k)
            aux['neu'] /= len(k)
            aux['compound'] /= len(k)
            comments.append(aux)
            comp_comments.append(aux_serie)
        else:
            comments.append({'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0})

    df.insert(len(df.columns), 'lexicon_text', phrases, True)
    df.insert(len(df.columns), 'lexicon_comments', comments, True)
    df.insert(len(df.columns), 'compound_phrases', comp_serie, True)
    df.insert(len(df.columns), 'compound_comments', comp_comments, True)
    return df


def build_lexicon_result(df: pd.DataFrame) -> pd.DataFrame:
    print("[LOG] Building lexicon result")
    lexicon = []
    for i in df.index:
        # + df.loc[i].lexicon_comments['compound']
        comp = df.loc[i].lexicon_text['compound']
        # print(">> ",comp)
        if comp <= -.05:
            lexicon.append('neg')
        elif comp >= .05:
            lexicon.append('pos')
        else:
            lexicon.append('neu')
    df.insert(len(df.columns), 'lexicon', lexicon, True)
    return df


def to_pickle_dataframe(df: pd.DataFrame, path: str):
    df.to_pickle(path)


def build_news_df():
    df = populate_dataframe()
    df = populate_lexicon_analysis(df)
    df = build_lexicon_result(df)
    to_pickle_dataframe(df, 'news.pkl')
    return df


def build_matches_df() -> pd.DataFrame:
    path = pathlib.Path('../data/matches/matches.json')
    js = json.load(path.open())

    data_frame = pd.DataFrame(columns=[
                              'id', 'date', 'attendance', 'income', 'id_winner', 'id_home_team', 'id_visiting_team'])
    counter = 0
    for i in js.keys():
        data_frame.loc[counter] = [i, js[i]['date'], js[i]['attendance'], js[i]['income'],
                                   js[i]['id_winner'], js[i]['id_home_team'], js[i]['id_visiting_team']]
        counter += 1
    to_pickle_dataframe(data_frame, 'matches.pkl')
    return data_frame


def build_statistics_df() -> pd.DataFrame:
    path = pathlib.Path('../data/statistics/statistics.json')
    js = json.load(path.open())
    data_frame = pd.DataFrame(columns=['team_id', 'match_id', 'status', 'shots', 'shots_on_goal', 'fouls',
                                       'offsides', 'ball_possession', 'corners', 'cross', 'yellow_cards', 'red_cards', 'goals'])
    counter = 0
    for i in js.keys():
        data_frame.loc[counter] = [js[i]['team_id'], js[i]['match_id'], js[i]
                                   ['status'], js[i]['shots'], js[i]['shots_on_goal'], js[i]['fouls'], js[i]['offsides'], js[i]['ball_possession'],
                                   js[i]['corners'], js[i]['cross'], js[i]['yellow_cards'], js[i]['red_cards'], js[i]['goals']]
        counter += 1
    to_pickle_dataframe(data_frame, 'statistics.pkl')
    return data_frame


def build_df_for_prediction() -> pd.DataFrame:
    matches = build_matches_df()
    stats = build_statistics_df()
    data_frame = pd.DataFrame(columns=['team_id_home', 'team_id_visiting', 'date', 'match_id', 'status_h', 'shots_h', 'shots_on_goal_h', 'fouls_h',
                                       'offsides_h', 'ball_possession_h', 'corners_h', 'cross_h', 'yellow_cards_h', 'red_cards_h', 'goals_h',  
                                       'status_v', 'shots_v', 'shots_on_goal_v', 'fouls_v',
                                       'offsides_v', 'ball_possession_v', 'corners_v', 'cross_v', 'yellow_cards_v', 'red_cards_v', 'goals_v'])
    for k in range(380):
        match = matches.query("id == '{}'".format(k)).to_numpy()
        data = []
        data.append(match[0][-2])
        data.append(match[0][-1])
        data.append(match[0][1])
        data.append(int(match[0][0]))
        home = stats.query("match_id == {} and status == 'h'".format(k)).to_numpy()
        for i in range(2, len(home[0])):
            if type(home[0][i]) == str:
                if home[0][i].isnumeric():
                    data.append(int(home[0][i]))
                else:
                    data.append(home[0][i])
            else:
                data.append(home[0][i])
        visiting = stats.query("match_id == {} and status == 'v'".format(k)).to_numpy()
        for i in range(2, len(home[0])):
            if type(visiting[0][i]) == str:
                if visiting[0][i].isnumeric():
                    data.append(int(visiting[0][i]))
                else:
                    data.append(visiting[0][i])
            else:
                data.append(visiting[0][i])

        data_frame.loc[k] = data
    classes = []
    for i in data_frame.index:
        if data_frame.loc[i].goals_h > data_frame.loc[i].goals_v:
            classes.append(0)
        elif data_frame.loc[i].goals_h < data_frame.loc[i].goals_v:
            classes.append(1)
        else:
            classes.append(2)
    data_frame.insert(len(data_frame.columns), 'classes', classes, True)
    to_pickle_dataframe(data_frame, 'data.pkl')
    return data_frame
# build_df_for_prediction()
# build_statistics_df()
# build_matches_df()



from datetime import datetime
def rodada(df: pd.DataFrame):
    # df = pd.read_pickle("data.pkl")
    print("[LOG] Buildind rounds")
    rodada = []
    for i in df.index:
        if datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('16/04/2018', "%d/%m/%Y"):
            rodada.append(1)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('23/04/2018', "%d/%m/%Y"):
            rodada.append(2)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('30/04/2018', "%d/%m/%Y"):
            rodada.append(3)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('07/05/2018', "%d/%m/%Y"):
            rodada.append(4)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('14/05/2018', "%d/%m/%Y"):
            rodada.append(5)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('21/05/2018', "%d/%m/%Y"):
            rodada.append(6)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('27/05/2018', "%d/%m/%Y"):
            rodada.append(7)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('31/05/2018', "%d/%m/%Y"):
            rodada.append(8)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('04/06/2018', "%d/%m/%Y"):
            rodada.append(9)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('07/06/2018', "%d/%m/%Y"):
            rodada.append(10)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('10/06/2018', "%d/%m/%Y"):
            rodada.append(11)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('13/06/2018', "%d/%m/%Y"):
            rodada.append(12)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('19/07/2018', "%d/%m/%Y"):
            rodada.append(13)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('23/07/2018', "%d/%m/%Y"):
            rodada.append(14)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('26/07/2018', "%d/%m/%Y"):
            rodada.append(15)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('30/07/2018', "%d/%m/%Y"):
            rodada.append(16)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('06/08/2018', "%d/%m/%Y"):
            rodada.append(17)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('13/08/2018', "%d/%m/%Y"):
            rodada.append(18)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('20/08/2018', "%d/%m/%Y"):
            rodada.append(19)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('23/08/2018', "%d/%m/%Y"):
            rodada.append(20)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('26/08/2018', "%d/%m/%Y"):
            rodada.append(21)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('02/09/2018', "%d/%m/%Y"):
            rodada.append(22)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('06/09/2018', "%d/%m/%Y"):
            rodada.append(23)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('10/09/2018', "%d/%m/%Y"):
            rodada.append(24)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('17/09/2018', "%d/%m/%Y"):
            rodada.append(25)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('24/09/2018', "%d/%m/%Y"):
            rodada.append(26)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('01/10/2018', "%d/%m/%Y"):
            rodada.append(27)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('09/10/2018', "%d/%m/%Y"):
            rodada.append(28)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('15/10/2018', "%d/%m/%Y"):
            rodada.append(29)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('22/10/2018', "%d/%m/%Y"):
            rodada.append(30)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('29/10/2018', "%d/%m/%Y"):
            rodada.append(31)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('05/11/2018', "%d/%m/%Y"):
            rodada.append(32)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('12/11/2018', "%d/%m/%Y"):
            rodada.append(33)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('15/11/2018', "%d/%m/%Y"):
            rodada.append(34)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('19/11/2018', "%d/%m/%Y"):
            rodada.append(35)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('22/11/2018', "%d/%m/%Y"):
            rodada.append(36)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('26/11/2018', "%d/%m/%Y"):
            rodada.append(37)
        elif datetime.strptime(df.loc[i].date, "%d/%m/%Y") <= datetime.strptime('02/12/2018', "%d/%m/%Y"):
            rodada.append(38)
        else:
            rodada.append(-1)
    print(len(rodada))
    df.insert(len(df.columns), 'round', rodada, True)
    to_pickle_dataframe(df, 'news.pkl')



def df_league():
    df = pd.read_pickle('data.pkl')
    teams = json.load(pathlib.Path('../data/teams.json').open())
    data = []
    for i in teams.keys():
        matches = 0
        goals_m = 0
        goals_s = 0
        goals_m_mean = 0
        goals_s_mean = 0
        aux = df.query("team_id_home == '{}'".format( list(teams[i].keys())[0] ))
        matches += len(aux)
        goals_m += aux.goals_h.sum()
        goals_s += aux.goals_v.sum()
        goals_m_mean += aux.goals_h.mean()
        goals_s_mean += aux.goals_v.mean()

        aux = df.query("team_id_visiting == '{}'".format( list(teams[i].keys())[0] ))
        matches += len(aux)
        goals_m += aux.goals_v.sum()
        goals_s += aux.goals_h.sum()
        goals_m_mean += aux.goals_v.mean()
        goals_s_mean += aux.goals_h.mean()

        goals_m_mean /= 2
        goals_s_mean /= 2
        matches /=2

        print("Time: ", teams[i][list(teams[i].keys())[0]])
        print("Jogos: ", matches)
        print("Gols marcados: ", goals_m)
        print("Média de gols marcados: ", goals_m_mean)
        print("Gols sofridos: ", goals_s)
        print("Média de gols sofridos: ", goals_s_mean)
        data.append([teams[i][list(teams[i].keys())[0]], matches, goals_m, goals_m_mean, goals_s, goals_s_mean])
    data_frame = pd.DataFrame(columns=["team", 'matches', 'goals_pro', 'mean_gp', 'goals_against', 'mean_ga'])
    for i in range(len(data)):
        data_frame.loc[i] = data[i]
    data_frame = data_frame.drop(20)

    sums = ['Total', data_frame.matches.sum(), data_frame.goals_pro.sum(),data_frame.mean_gp.sum(), data_frame.goals_against.sum(), data_frame.mean_ga.sum()]
    avg = ['Average', data_frame.matches.mean(), data_frame.goals_pro.mean(),data_frame.mean_gp.mean(), data_frame.goals_against.mean(), data_frame.mean_ga.mean()]
    data_frame.loc[20] = sums
    data_frame.loc[21] = avg
    to_pickle_dataframe(data_frame, 'league.pkl')



# df_league()
df = build_news_df()
rodada(df)