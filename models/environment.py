import numpy as np
import pandas as pd
import time

from agent import Agent


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
            LSTM_inputs.append(df[i:(i+memory_len)])

        LSTM_inputs = [np.array(LSTM_input) for LSTM_input in LSTM_inputs]
        LSTM_inputs = np.array(LSTM_inputs)
        LSTM_inputs = np.reshape(LSTM_inputs, (LSTM_inputs.shape[0], 1, LSTM_inputs.shape[1]))
        # Select the correct data
        if (training):
            return LSTM_inputs[0:int(len(df)*0.5)]
        else:
            return LSTM_inputs[int(len(df)*0.5)+1:]


def train_agent(memory_len=100, epochs=50, model_name="dqn"):
    """
    Function responsible for training the model.

    :memory_len: number of previous stock prices use for analysis
    :epochs: number of episodes of learning
    :model_name: path of the saved model

    :return: agent
    """
    # Get the training data
    agent = Agent(process_data(get_data('Stocks/goog.us.txt'), memory_len, True), False, model_name, memory_len)

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
            next_state = agent.data[t+1]
            # Make a decision
            decision = agent.decision(state)
            # Perform the action
            reward = agent.step(decision)
            # Save the observations
            agent.memory.append((state, next_state, decision, reward, agent.done))
            # Learn after a certain number of iterations
            if (e + 1) * (t + 1) % agent.batch_size == 0:
                total_error += agent.learn()

            total_reward += reward

        total_rewards.append(total_reward)
        total_errors.append(total_error)

        # Save the model
        if e % 10 == 0:
            agent.model.save(agent.model_name + str(e))

        # Log
        if (e+1) % show_log_freq == 0:
            # Average the last few (show_log_freq) rewards and errors
            log_reward = sum(total_rewards[((e + 1) - show_log_freq):]) / show_log_freq
            log_error = sum(total_errors[((e + 1) - show_log_freq):]) / show_log_freq
            elapsed_time = time.time()-start
            print('\t'.join(map(str, [e+1, "{0:02f}".format(agent.epsilon), "{0:02f}".format(agent.profit),
                        "{0:02f}".format(log_reward), "{0:02f}".format(log_error), "{0:02f}".format(elapsed_time)])))
            start = time.time()

    return agent


def evaluate_agent():
    """
    Function responsible for testing the model.
    """
    # Get the training data
    agent.data = process_data(get_data('Stocks/goog.us.txt'), agent.input_space, False)

    l = len(agent.data) - 1
    # Set testing mode
    agent.reset()

    # For each data point
    for t in range(l):
        # Get the last few stock prices
        state = agent.data[t]
        # Make a decision
        decision = agent.decision(state)
        # Perform the action
        reward = agent.step(decision)

    print("--------------------------------")
    print(agent.profit)
    print("--------------------------------")

if __name__ == '__main__':
    agent = train_agent()
    evaluate_agent()
