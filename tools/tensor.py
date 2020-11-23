import tensorflow as tf
import pandas as pd
import numpy as np
df = pd.read_pickle('mlp_data.pkl')
compound_h, compound_v = [], []
for i in df.index:
    compound_h.append(df.loc[i].compound_h * 100)
    compound_v.append(df.loc[i].compound_v * 100)

df.compound_h = compound_h
df.compound_v = compound_v
# print(df)
# input()


def build_data(df):
    features = ['prob_w', 'prob_d', 'prob_l', 'compound_h', 'compound_v']
    training_data = (tf.data.Dataset.from_tensor_slices(
        (
            tf.cast(df[features].astype(float).values , tf.float32),
            tf.cast(df['result'].astype(float).values, tf.float32)
        )
    ))
    data = []
    target = []
    for features_tensor, target_tensor in training_data:
        data.append(features_tensor)
        target.append(target_tensor)
        # print(f'features:{features_tensor} target:{target_tensor}')
        # input()
    return np.array(data), np.array(target)

evaluate = []
counter = 0
model = tf.keras.models.Sequential([
    # tf.keras.layers.Flatten(input_shape=(5,)),
    tf.keras.layers.Dense(512, activation='sigmoid'),
    # tf.keras.layers.Dropout(0.2),
    # tf.keras.layers.Dense(10, activation='relu')
    ])
for i in range(10):
    model.add(tf.keras.layers.Dense(200, activation='tanh'))
# model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(5, activation='softmax'))
# tf.keras.optimizers.Adamax
# tf.keras.optimizers.RMSprop
#Adam
model.compile(optimizer='adadelta',
            loss=tf.keras.losses.sparse_categorical_crossentropy,
            # loss=tf.keras.losses.sparse_categorical_crossentropy,
            metrics=['accuracy'])
for i in range(3, 38):
    #Train: 
    df_train = df.query("round < {}".format(i))
    x_train, y_train = build_data(df_train)
    #Tesst:
    df_test = df.query("round == {}".format(i))
    x_test, y_test = build_data(df_test)
    


    model.fit(x_train, y_train, epochs = 20)
    evaluate.append(model.evaluate(x_test, y_test, verbose=2)[1])
    counter += 1

print(f"Final acc: {(sum(evaluate)/counter) * 100}")

for i in range(len(evaluate)):
    print(f"Round {i+3} | acc: {evaluate[i]}")



# model.fit(data, data.)


    """Final acc: 56.313853881188805
Round 3 | acc: 0.2222222238779068
Round 4 | acc: 0.30000001192092896
Round 5 | acc: 0.6000000238418579
Round 6 | acc: 0.20000000298023224
Round 7 | acc: 0.5
Round 8 | acc: 0.800000011920929
Round 9 | acc: 0.4000000059604645
Round 10 | acc: 0.6000000238418579
Round 11 | acc: 0.6000000238418579
Round 12 | acc: 0.6000000238418579
Round 13 | acc: 0.6000000238418579
Round 14 | acc: 0.699999988079071
Round 15 | acc: 0.625
Round 16 | acc: 0.699999988079071
Round 17 | acc: 0.10000000149011612
Round 18 | acc: 0.7272727489471436
Round 19 | acc: 0.6000000238418579
Round 20 | acc: 0.5
Round 21 | acc: 0.6000000238418579
Round 22 | acc: 0.5
Round 23 | acc: 0.6000000238418579
Round 24 | acc: 0.699999988079071
Round 25 | acc: 0.8181818127632141
Round 26 | acc: 0.6000000238418579
Round 27 | acc: 0.6363636255264282
Round 28 | acc: 0.4444444477558136
Round 29 | acc: 0.6000000238418579
Round 30 | acc: 0.6000000238418579
Round 31 | acc: 0.6363636255264282
Round 32 | acc: 0.6000000238418579
Round 33 | acc: 0.6000000238418579
Round 34 | acc: 0.6000000238418579
Round 35 | acc: 0.6000000238418579
Round 36 | acc: 0.800000011920929
Round 37 | acc: 0.4000000059604645

    """