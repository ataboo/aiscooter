import numpy as np
import pandas as pd
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.utils import to_categorical
import random

class Config(object):
    def __init__(self, input_count, output_count):
        self.input_count = input_count
        self.output_count = output_count
        self.epsilon = 0.5

class DQNAgent(object):
    def __init__(self, config: Config):
        self.reward = 0
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = 0.0005
        self.epsilon = config.epsilon
        self.actual = []
        self.memory = []
        self.input_count = config.input_count
        self.out_count = config.output_count
        self.model = self.network()
        self.max_memory = 100000

    def network(self, weights=None):
        model = Sequential()
        model.add(Dense(units=256, activation='relu', input_dim=self.input_count))
        model.add(Dropout(0.4))
        model.add(Dense(units=256, activation='relu'))
        model.add(Dropout(0.4))
        model.add(Dense(units=256, activation='relu'))
        model.add(Dropout(0.4))
        model.add(Dense(units=self.out_count, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if weights:
            model.load_weights(weights)
        return model

    def copy_weights_to(self, agent):
        agent.model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def replay_new(self, memory):
        if len(memory) > 1000:
            minibatch = random.sample(memory, 1000)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

    def train_short_memory(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, self.input_count)))[0])
        target_f = self.model.predict(state.reshape((1, self.input_count)))
        target_f[0][np.argmax(action)] = target
        self.model.fit(state.reshape((1, self.input_count)), target_f, epochs=1, verbose=0)

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return to_categorical(random.randint(0, self.out_count-1), num_classes=self.out_count)

        prediction = self.model.predict(state.reshape((1, self.input_count)))
        return to_categorical(np.argmax(prediction[0]), num_classes=self.out_count)

