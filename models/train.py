from agent import Agent


def get_data():
	data = pd.read_csv('../input/Data/Stocks/goog.us.txt')
	data['Date'] = pd.to_datetime(data['Date'])
	return data.set_index('Date')


def train_agent(epochs=50, model_name="dqn"):
	agent = Agent(get_data(), model_name=model_name)

	l = len(agent.data) - 1
    total_rewards = []
    total_losses = []
	show_log_freq = 5

	start = time.time()
	# Repeat for a number of epochs
	for e in range(epochs):
		# Reset the agent at the begining of each epoch
		agent.reset()
		# For each data point
		for t in range(l):
			total_error, total_reward = 0
			# Make a decision
			decision = agent.decision(state) # TODO: get state function
			# Do the action
			_, reward, done = agent.step(action)
			# Save the observations
			agent.memory.append((state, decision, reward, done))
			# Learn after a certain number of iterations
			if (e + 1) * (t + 1) % agent.batch_size == 0:
				total_error += agent.learn()

			# next step
            total_reward += reward

        total_rewards.append(total_reward)
        total_losses.append(total_loss)

		if e % 10 == 0:
			agent.model.save(self.model_name + str(e))

		if (epoch+1) % show_log_freq == 0:
            log_reward = sum(total_rewards[((epoch+1)-show_log_freq):])/show_log_freq
            log_loss = sum(total_losses[((epoch+1)-show_log_freq):])/show_log_freq
            elapsed_time = time.time()-start
            print('\t'.join(map(str, [epoch+1, epsilon, total_step, log_reward, log_loss, elapsed_time])))
            start = time.time()
