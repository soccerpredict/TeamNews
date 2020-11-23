import pandas as pd
import sentiment
import poisson
from sklearn.neural_network import MLPClassifier
from pathlib import Path
import json
from sklearn.model_selection import train_test_split

def who_win(df):
    print((df.goals_h, df.goals_v))
    if df.goals_h > df.goals_v:
        return 0
    elif df.goals_v > df.goals_h:
        return 2
    else:
        return 1

def build():
    p = Path('rounds_sentiment/').glob("*.json")
    p = list(p)
    print(p)
    df = pd.DataFrame(columns=['mandant', 'visitant', 'prob_w', 'prob_d',
                               'prob_l', 'compound_h', 'compound_v', 'round', 'result'])
    data = []
    counter = 0
    for i in p:
        print(i.name)
        js = json.load(i.open())
        for k in js.keys():
            # print(js[k])
            df.loc[counter] = [js[k]['mandant'], js[k]['visitant'], js[k]['predictions'][0], js[k]['predictions'][1], js[k]['predictions'][2],
                              js[k]['percent_mandant'], js[k]['percent_visitant'], int(i.name.split('_')[1].split('.')[0]), int(js[k]['result'])]
            # print(data)
            counter += 1
    df.to_pickle('mlp_data.pkl')


def split_less(df, round):
    classes = df.query('round < {}'.format(round)).result
    c = []
    for i in classes:
        if i == 1:
            c.append('draw')
        if i == 0:
            c.append('win')
        if i == 2:
            c.append('lose')
    # print(classes.to_numpy())
    return df.query('round < {}'.format(round)).drop(columns=['mandant', 'visitant', 'result', 'round']), c

def split_equal(df, round):
    classes = df.query('round == {}'.format(round)).result
    c = []
    for i in classes:
        if i == 1:
            c.append('draw')
        if i == 0:
            c.append('win')
        if i == 2:
            c.append('lose')
    # print(classes.to_numpy())
    return df.query('round == {}'.format(round)).drop(columns=['mandant', 'visitant', 'result', 'round']), c
# build()

df = pd.read_pickle('mlp_data.pkl')
compound_h, compound_v = [], []
for i in df.index:
    compound_h.append(df.loc[i].compound_h * 100)
    compound_v.append(df.loc[i].compound_v * 100)

df.compound_h = compound_h
df.compound_v = compound_v

# print(r2, '\n', classes)

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

mlp = MLPClassifier(random_state=42, max_iter=5000, activation='logistic')
tree = DecisionTreeClassifier(random_state=42)
svm = SVC(random_state=42)
rf = RandomForestClassifier(random_state=42)
# mlp.fit(r2, classes)

# r3, class3 = df_split(df, 3)
# print(mlp.score(r3.to_numpy(), class3))

mlp_scores = []
tree_scores = []
svm_scores = []
rf_scores = []
counter = 0
for i in range(3, 38):
    x_train, y_train = split_less(df, i)
    x_test, y_test = split_equal(df, i)
    mlp.fit(x_train, y_train)
    tree.fit(x_train, y_train)
    svm.fit(x_train, y_train)
    rf.fit(x_train, y_train)
    
    print("Score round {} >> MLP: {} | Tree: {} | SVM: {} | Random Forest: {}".format(i, mlp.score(x_test, y_test), tree.score(x_test, y_test), svm.score(x_test, y_test), rf.score(x_test, y_test)))
    mlp_scores.append(mlp.score(x_test, y_test))
    tree_scores.append(tree.score(x_test, y_test))
    svm_scores.append(svm.score(x_test, y_test))
    rf_scores.append(svm.score(x_test, y_test))
    counter += 1
print("Final score MLP: {}".format(sum(mlp_scores)/counter))
print("Final score Tree: {}".format(sum(tree_scores)/counter))
print("Final score SVM: {}".format(sum(svm_scores)/counter))
print("Final score Random Forest: {}".format(sum(rf_scores)/counter))

# build_data()
