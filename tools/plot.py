import matplotlib.pyplot as plt
import sentiment
import pandas as pd

def build_goals_score(team):
    df = pd.read_pickle('data.pkl')
    matches = df.query("team_id_visiting == '{}' or team_id_home == '{}'".format(team, team))
    matches = matches.sort_values(by=['round'])
    # print(matches)
    data = []
    for k in matches.index:
        if matches.loc[k].team_id_home == team:
            data.append(matches.loc[k].goals_h - matches.loc[k].goals_v)
        else:
            data.append(matches.loc[k].goals_v - matches.loc[k].goals_h)
    print(len(data))
    return data

def build_compound_score(team):
    df = pd.read_pickle('data.pkl')
    matches = df.query("team_id_visiting == '{}' or team_id_home == '{}'".format(team, team))
    matches = matches.sort_values(by=['round'])
    sent = sentiment.SentimentPredictor()
    data = []
    for i in matches.index:
        data.append(sent.favg_round(team, matches.loc[i]['round']))
    print(len(data))
    return data
    




goals_score = build_goals_score('sao_paulo')
compound = build_compound_score('sao_paulo')
print(compound)
compound = [i*100 for i in compound]

plt.plot(goals_score, label='Goals score')
plt.plot(compound, label='Compound')
plt.legend()
plt.xlabel('Rodada')
plt.ylabel("Saldo de Gols e Compound")
plt.title("Saldo de gols e AVG Compound por rodada do São Paulo")
plt.savefig("goals_avg_compound_sao_paulo.png")
plt.show()
# plt.scatter(list(range(1, 39)), goals_score )
# plt.title("Saldo de gols por rodada do Atlético MG")
# plt.savefig("goals_score_scatter_atletico_mg.png")
# plt.show()

# plt.scatter(list(range(1, 39)), compound )
# plt.xlabel('Rodada')
# plt.ylabel("Avg Compound")
# plt.title("Avg Compound por rodada do Atlético MG")
# plt.savefig("compound_score_scatter_atletico_mg.png")
# plt.show()

