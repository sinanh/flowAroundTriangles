# -*- coding: utf-8 -*-

import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, Sequential
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np

# Load the dataframe that was saved in read_files.py
# df = pd.read_csv("tmp/df.csv",index_col=0)
df = pd.read_csv("tmp/training_data.csv", sep="\t")

print(df.tail())
# Split data into train and test sets
train, test = train_test_split(df, test_size=0.2)
# Create a shallow copy of the data
train_features = train.copy()
test_features = test.copy()

#labels = ['mean Cd 200', 'mean Cd 400', 'mean Cd 600']

labels = ['cd', 'cl']

# Remove the "mean Cd" column from the features and use it as label
train_labels = pd.concat([train_features.pop(x) for x in labels ], axis=1)
#train_labels = train_features.pop('mean Cd')
test_labels = pd.concat([test_features.pop(x) for x in labels], axis=1)

# 8 layers with 32 nodes in each layer was found as good set-up using
# the parameter_study.py script
n_layers = 8
n_nodes = 32

all_layers = [layers.Dense(n_nodes, activation="relu", name="hidden_layer_"+str(i)) for i in np.arange(n_layers)]
all_layers.append(layers.Dense(2, name="output_layer"))
model = Sequential(all_layers)

# Compile the model to static graph
model.compile(optimizer="Adam", loss='mean_squared_error')

# Train the model using 80% of the training data
history = model.fit(
    train_features, train_labels,
    epochs=400,
    # Calculate validation results on 20% of the training data
    validation_split = 0.2)

# Test the model on up to now unused test data
# Loss on test data should be close to loss on
# on validation data during training, otherwise
# the model is overfitted
print("==================================================================")
print("===============================Test===============================")
eval_loss = model.evaluate(test_features,test_labels)

# Plot history of train and validation loss
plt.figure()
plt.semilogy(history.history['loss'])
plt.semilogy(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train loss', 'validation loss'], loc='upper left')
plt.savefig("model_loss_"+str(n_nodes)+"_nodes_"+str(n_layers)+"_layer.png")

# Test model prediction
model.predict(x=[[15,21,15,15,21,23]])

# Save the model for later use
model.save('tmp/model')
