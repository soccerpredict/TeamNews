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
            aux = [data[i]['time'], data[i]['date'], data[i]['title'], data[i]['author'], data[i]['text'],
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

# build_statistics_df()
# build_matches_df()
