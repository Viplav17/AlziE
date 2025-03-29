from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import numpy as np
import pandas as pd

X = np.array([
    [111, 158, -0.4],
    [142, 163, -0.9],
    [126, 128, 0.1],
    [144, 160, -0.7],
    [119, 130, 0.6],
    [98, 159, 0.9],
    [129, 139, -0.2],
    [98, 130, -0.1],
    [103, 105, -0.8],
    [121, 148, 0.9],
    [132, 123, -0.6],
    [125, 141, 0.5],
    [140, 125, -0.7]



])


from sklearn.model_selection import train_test_split

# Labels (same as before)
y = np.array([0.5, 0.9, 0, 0.9, 0, 0, 0.3, 0, 0.5, 0, 0.7, 0.3, 0.7])

# Split dataset (80% training, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the model with 3 input features
model = Sequential([
    Input(shape=(3,)),  # Change input shape from (4,) to (3,)
    Dense(8, activation='relu'),  # First hidden layer with 8 neurons
    Dense(4, activation='relu'),  # Second hidden layer with 4 neurons
    Dense(1, activation='linear')  # Output layer (for percentage prediction)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

# Print model summary
model.summary()

#Compile
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=4, validation_data=(X_test, y_test))

test_loss, test_mae = model.evaluate(X_test, y_test)
print(f"Test Loss: {test_loss}, Test MAE: {test_mae}")

from Sentiment_analysis import polarity_value
polarity = polarity_value()

# Make a prediction
sample = np.array([[85, 250, polarity]])  # Example input

prediction = model.predict(sample)

print(f"Panic Attack Probability: {prediction[0][0]*100:.2f}%")