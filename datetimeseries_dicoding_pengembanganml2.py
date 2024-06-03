# -*- coding: utf-8 -*-
"""DateTimeSeries_Dicoding_PengembanganML2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KF6ocN79FbcZEiks4gIwuSRHHZtRD5Wo

NAMA : Derajat Salim Wibowo
NIM  : 2210511077
Asal : UPN Veteran Jakarta - Teknik Informatika
"""

#Memanggil Library
import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# mengambil dataset dari Google Drive
df = pd.read_csv('/content/drive/MyDrive/ML/AMD(1980-11.07.2023).csv')

df.head()

#menampilkan jumlah sampel dataset
df.shape

df.isnull().sum()

dates = df['Date'].values
volume = df['Volume'].values
plt.figure(figsize=(20, 10))
plt.plot(dates, volume)
plt.title('Saham Terjual', fontsize=20)
plt.show()

df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df['Volume'].values.reshape(-1, 1))
scaled_data = scaled_data.flatten()

X_train, X_test = train_test_split(scaled_data, test_size=0.2, shuffle=False)
print(len(X_train), len(X_test))

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(X_train, window_size=60, batch_size=100, shuffle_buffer=1000)
val_set  = windowed_dataset(X_test, window_size=60, batch_size=32, shuffle_buffer=1000)

model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(60, return_sequences=True, input_shape = [None, 1]),
  tf.keras.layers.LSTM(60),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

batas_mae = (scaled_data.max() - scaled_data.min()) * (10 / 100)

class callbacks(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae') < batas_mae):
      print('MAE < 10% skala data')
      self.model.stop_training = True

callbacks = callbacks()

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(
    loss=tf.keras.losses.Huber(),
    optimizer = optimizer,
    metrics=['mae']
)

history = model.fit(
    train_set,
    epochs=30,
    validation_data=val_set,
    verbose=2,
    callbacks=[callbacks],
)