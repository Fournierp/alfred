from agent import Agent

import numpy as np
import pandas as pd


def get_data(path):
    """
    Get a company's stock price history, extract the Closing price and index it by day.

    :path: path to the company's data

    :return: data
    """
    data = pd.read_csv(path)
    data['Date'] = pd.to_datetime(data['Date'])
    return data.set_index('Date')["Close"]


def process_data(df, memory_len, training):
        """
        Create individual series of 10 Closing prices.

        :df: raw data
        :memory_len: size of the series
        :training: boolean to determine whether to give training or testing data.

        :return: array of series of stock prices
        """
        LSTM_inputs = []
        for i in range(len(df) - memory_len):
#             LSTM_inputs.append(df[i:(i+memory_len)])

            tmp_df = df[i:(i+memory_len)].copy()
            tmp_df = tmp_df/tmp_df.iloc[0] - 1
            LSTM_inputs.append(tmp_df)

        LSTM_inputs = [np.array(LSTM_input) for LSTM_input in LSTM_inputs]
        LSTM_inputs = np.array(LSTM_inputs)
        LSTM_inputs = np.reshape(LSTM_inputs, (LSTM_inputs.shape[0], 1, LSTM_inputs.shape[1]))
        # Select the correct data
        if (training):
            return LSTM_inputs[0:int(len(df)*0.8)]
        else:
            return LSTM_inputs[int(len(df)*0.8)+1:]


def train_agent(memory_len=10, epochs=50, model_name="dqn"):
    """
    Function responsible for feeding data to the model,
    """
    # Get the training data
    agent = Agent(process_data(get_data('../input/Data/Stocks/goog.us.txt'), memory_len, True), False, model_name, memory_len)

    l = len(agent.data) - 1
    total_rewards = []
    total_errors = []
    show_log_freq = 5

    start = time.time()
    # Repeat for a number of epochs
    for e in range(epochs):
        total_error = total_reward = 0
        # Reset the agent at the begining of each epoch
        agent.reset()
        # For each data point
        for t in range(l):
            # Get the last few stock prices
            state = agent.data[t]
            # Make a decision
            decision = agent.decision(state)
            # Perform the action
            reward = agent.step(decision)
            # Save the observations
            agent.memory.append((state, decision, reward, agent.done))
            # Learn after a certain number of iterations
            if (e + 1) * (t + 1) % agent.batch_size == 0:
                total_error += agent.learn()

            total_reward += reward

        total_rewards.append(total_reward)
        total_errors.append(total_error)

        # Save the model
        if e % 10 == 0:
            agent.model.save(self.model_name + str(e))

        # Log
        if (e+1) % show_log_freq == 0:
            # Average the last few (show_log_freq) rewards and errors
            log_reward = sum(total_rewards[((e + 1) - show_log_freq):]) / show_log_freq
            log_error = sum(total_errors[((e + 1) - show_log_freq):]) / show_log_freq
            elapsed_time = time.time()-start
            print('\t'.join(map(str, [e+1, agent.epsilon, log_reward, log_error, elapsed_time])))
            start = time.time()

train_agent()
