# Import necessary libraries
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
from art import text2art
from dotenv import load_dotenv
from collections import Counter

class LotteryAi:
    data_dir = ''
    model_dir = ''
    def __init__(self):
        # Initialize any variables you need here
        load_dotenv()
        self.data_dir = os.getenv('STORE_DIR')
        self.model_dir = os.getenv('MODEL_DIR')
        pass

    # Function to print the introduction of the program
    def print_intro(self, model_name):
        # Generate ASCII art with the text "LotteryAi"
        ascii_art = text2art(model_name)
        # Print the introduction and ASCII art
        print("============================================================")
        print("LotteryAi")
        print("============================================================")
        print(ascii_art)
        print("Lottery prediction artificial intelligence")

    # Function to load data from a file and preprocess it
    def load_data(self, model_name):
        # Load data from file, ignoring white spaces and accepting unlimited length numbers
        data = np.genfromtxt(self.data_dir + '/' + model_name + '.csv', delimiter=',', dtype=int)
        # Replace all -1 values with 0
        data[data == -1] = 0
        # Split data into training and validation sets
        train_data = data[:int(0.8*len(data))]
        val_data = data[int(0.8*len(data)):]
        # Get the maximum value in the data
        max_value = np.max(data)
        return train_data, val_data, max_value

    # Function to create the model
    def create_model(self, num_features, max_value):
        # Create a sequential model
        model = keras.Sequential()
        # Add an Embedding layer, LSTM layer, and Dense layer to the model
        model.add(layers.Embedding(input_dim=max_value+1, output_dim=64))
        model.add(layers.LSTM(256))
        model.add(layers.Dense(num_features, activation='softmax'))
        # Compile the model with categorical crossentropy loss, adam optimizer, and accuracy metric
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    # Function to train the model
    def train_model(self, model_name):
        
        # Load and preprocess data 
        train_data, val_data, max_value = self.load_data(model_name)
        
        # Get number of features from training data 
        num_features = train_data.shape[1]

        # Create and compile model 
        model = self.create_model(num_features, max_value)

        # Fit the model on the training data and validate on the validation data for 100 epochs
        history = model.fit(train_data, train_data, validation_data=(val_data, val_data), epochs=100)

        # Create the model directory if it does not exist
        if not os.path.exists(self.model_dir):
            os.mkdir(self.model_dir)

        # Delete the previous model file if it exists
        model_file = f'{self.model_dir}/{model_name}.keras'
        if os.path.exists(model_file):
            os.remove(model_file)

        # Save the model to a file
        model.save(model_file)

        # Get the validation accuracy from the history
        val_accuracy = history.history['val_accuracy'][-1]
        with open(f'{self.model_dir}/{model_name}_val_accuracy.txt', 'w') as f:
            f.write(str(val_accuracy))


    # Function to predict numbers using the trained model
    def predict_numbers(self, model, val_data, num_features):
        # Predict on the validation data using the model
        predictions = model.predict(val_data)
        # Get the indices of the top 'num_features' predictions for each sample in validation data
        indices = np.argsort(predictions, axis=1)[:, -num_features:]
        # Get the predicted numbers using these indices from validation data
        predicted_numbers = np.take_along_axis(val_data, indices, axis=1)
        return predicted_numbers

    # Function to print the predicted numbers
    def print_predicted_numbers(self, predicted_numbers):
        # Print a separator line and "Predicted Numbers:"
        print("============================================================")
        print("Predicted Numbers:")
        # Print only the first row of predicted numbers
        print(', '.join(map(str, predicted_numbers[0])))
        print("============================================================")

    # Main function to run everything   
    def train(self, model_name):
        # Print introduction of program 
        self.print_intro(model_name)

        # Train model 
        self.train_model(model_name)

    # Main function to run everything   
    def predict(self, model_name, number_of_future=None):
        # Load and preprocess data 
        train_data, val_data, max_value = self.load_data(model_name)

        if number_of_future == None or 'vietlot-655'.__eq__(model_name):
            num_features = train_data.shape[1]
        else:
            num_features = number_of_future

        # Load the model from a file
        model_file = f'{self.model_dir}/{model_name}.keras'
        print('model_file: ', model_file)
        model = keras.models.load_model(model_file)

        # Predict numbers using trained model 
        predicted_numbers = self.predict_numbers(model, val_data, num_features)
        res = predicted_numbers[0]

        # Convert the predicted numbers to a list of strings
        return [str(num) for num in res]

    def deep_predict(self, model_name, number_of_future=None):
        basePrediction = self.predict(model_name, None, None)
        if number_of_future == None or 'vietlot-655'.__eq__(model_name):
            return basePrediction

        # prediction has format like 10(0%) I want extract the number only
        prediction = [pred.split('(')[0] for pred in basePrediction]
        # convert prediction to int
        prediction = [int(pred) for pred in prediction]
        # sort the prediction
        prediction = sorted(prediction)
        # count the appear time of each number in prediction
        predictionCounter = Counter(prediction)
        # get all number has the appear time equals to the most common number in prediction
        most_common_prediction = [pred for pred in prediction if predictionCounter[pred] == predictionCounter.most_common(1)[0][1]]
        # distinct the most_common_prediction
        most_common_prediction = list(set(most_common_prediction))

        # Load and preprocess data 
        train_data, val_data, max_value = self.load_data(model_name)

        # Flatten val_data from 2D list to 1D list
        flat_val_data = [item for sublist in val_data for item in sublist]

        # Count the occurrences of each number in prediction in flat_val_data
        counter = Counter(flat_val_data)

        # with each prediction number, get the number of times it appears based on counter in format number:count
        most_common_nums = [f'{pred}:{counter[pred]}' for pred in most_common_prediction]

        # sort the most_common_nums by count descending
        most_common_nums = sorted(most_common_nums, key=lambda x: int(x.split(':')[1]), reverse=True)

        # find the number_of_future in most_common_nums
        if len(most_common_nums) == 0:
            return []
        if len(most_common_nums) > number_of_future:
            most_common_nums = most_common_nums[:number_of_future]

        # remove semicolon on each item
        most_common_nums = [item.split(':')[0] for item in most_common_nums]

        return most_common_nums
