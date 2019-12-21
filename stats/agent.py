import pkg_resources
import types
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from IPython import display
import math
from pprint import pprint
import pandas as pd
import numpy as np
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
import praw
sns.set(style='darkgrid', context='talk', palette='Dark2')
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

def reddit_analysis():
    # nltk.download('vader_lexicon')
    reddit = praw.Reddit(client_id='7jUlWSWelE0zpg',
                         client_secret='V8W2JZJs05cYOFCRb6oMTN7TXvY',
                         user_agent='cyberdhirendra')
    headlines = set()
    for submission in reddit.subreddit('Amazon').new(limit=None):
        headlines.add(submission.title)
        display.clear_output()
    from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

    sia = SIA()
    results = []

    for line in headlines:
        pol_score = sia.polarity_scores(line)
        pol_score['headline'] = line
        results.append(pol_score)

    dtf = pd.DataFrame.from_records(results)
    dtf['label'] = 0
    dtf.loc[dtf['compound'] > 0.2, 'label'] = 1
    dtf.loc[dtf['compound'] < -0.2, 'label'] = -1
    counts = dtf.label.value_counts(normalize=True) * 100
    return counts[-1]
neg = reddit_analysis()

class Deep_Evolution_Strategy:
    inputs = None
    def __init__(
        self, weights, reward_function, population_size, sigma, learning_rate
    ):
        self.weights = weights
        self.reward_function = reward_function
        self.population_size = population_size
        self.sigma = sigma
        self.learning_rate = learning_rate

    def _get_weight_from_population(self, weights, population):
        weights_population = []
        for index, i in enumerate(population):
            jittered = self.sigma * i
            weights_population.append(weights[index] + jittered)
        return weights_population

    def get_weights(self):
        return self.weights

    def train(self, epoch = 100, print_every = 1):
        lasttime = time.time()
        for i in range(epoch):
            population = []
            rewards = np.zeros(self.population_size)
            for k in range(self.population_size):
                x = []
                for w in self.weights:
                    x.append(np.random.randn(*w.shape))
                population.append(x)
            for k in range(self.population_size):
                weights_population = self._get_weight_from_population(
                    self.weights, population[k]
                )
                rewards[k] = self.reward_function(weights_population)
            rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-7)
            for index, w in enumerate(self.weights):
                A = np.array([p[index] for p in population])
                self.weights[index] = (
                    w
                    + self.learning_rate
                    / (self.population_size * self.sigma)
                    * np.dot(A.T, rewards).T
                )
            if (i + 1) % print_every == 0:
                print('iter %d. reward: %f'% (i + 1, self.reward_function(self.weights)))
        print('time taken to train:', time.time() - lasttime, 'seconds')


class Model:
    def __init__(self, input_size, layer_size, output_size):
        self.window_size = input_size
        self.weights = [
            np.random.randn(input_size, layer_size),
            np.random.randn(layer_size, output_size),
            np.random.randn(1, layer_size),
        ]

    def predict(self, inputs):
        feed = np.dot(inputs, self.weights[0]) + self.weights[-1]
        decision = np.dot(feed, self.weights[1])
        return decision

    def get_weights(self):
        return self.weights

    def set_weights(self, weights):
        self.weights = weights


class Agent:
    POPULATION_SIZE = 15
    SIGMA = 0.1
    LEARNING_RATE = 0.03


    def __init__(self, model, window_size, trend, skip, initial_money, perc=10):
        self.model = model
        self.window_size = window_size
        self.half_window = window_size // 2
        self.trend = trend
        self.skip = skip
        self.initial_money = initial_money
        self.perc = perc
        self.es = Deep_Evolution_Strategy(
            self.model.get_weights(),
            self.get_reward,
            self.POPULATION_SIZE,
            self.SIGMA,
            self.LEARNING_RATE,
        )

    def act(self, sequence):
        decision = self.model.predict(np.array(sequence))
        return np.argmax(decision[0])

    def get_state(self, t):
        window_size = self.window_size + 1
        d = t - window_size + 1
        block = self.trend[d: t + 1] if d >= 0 else -d * [self.trend[0]] + self.trend[0: t + 1]
        res = []
        for i in range(window_size - 1):
            res.append(block[i + 1] - block[i])
        return np.array([res])

    def get_reward(self, weights):
        initial_money = self.initial_money
        starting_money = initial_money
        self.model.weights = weights
        state = self.get_state(0)
        inventory = []
        quantity = 0
        for t in range(0, len(self.trend) - 1, self.skip):
            action = self.act(state)
            next_state = self.get_state(t + 1)

            if action == 1 and starting_money >= self.trend[t]:
                inventory.append(self.trend[t])
                starting_money -= close[t]

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                starting_money += self.trend[t]

            state = next_state
        return ((starting_money - initial_money) / initial_money) * 100

    def fit(self, iterations, checkpoint):
        self.es.train(iterations, print_every=checkpoint)

    def buy(self, start_index=0):
        initial_money = self.initial_money
        state = self.get_state(0)
        starting_money = initial_money
        states_sell = []
        states_buy = []
        inventory = []
        for t in range( start_index, len(self.trend) - 1, self.skip):
            action = self.act(state)
            next_state = self.get_state(t + 1)

            if action == 1 and initial_money >= self.trend[t] and neg<50:
                inventory.append(self.trend[t])
                initial_money -= self.trend[t]
                states_buy.append(t)
                print('day %d: buy 1 unit at price %f, total balance %f' % (t, self.trend[t], initial_money))

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                initial_money += self.trend[t]
                states_sell.append(t)
                try:
                    invest = ((close[t] - bought_price) / bought_price) * 100
                except:
                    invest = 0
                print(
                    'day %d, sell 1 unit at price %f, investment %f %%, total balance %f,'
                    % (t, close[t], invest, initial_money)
                )
            state = next_state

        invest = ((initial_money - starting_money) / starting_money) * 100
        total_gains = initial_money - starting_money
        return states_buy, states_sell, total_gains, invest



def make_model(company, window_size=30, start="2019-04-01"):

    print(start)

    df_full = pdr.get_data_yahoo(company, start=start).reset_index()
    #df_full.to_csv('output/'+company+'.csv',index=False)
    #df_full = pd.read_csv('output/'+company+'.csv')

    model = Model(input_size = window_size, layer_size = 500, output_size = 3)
    model.df = df_full.copy()
    return model

def make_agent(model, initial_money=10000, iterations=500, checkpoint=10):
    window_size = model.window_size
    df = model.df
    global close
    close = df.Close.values.tolist()
    skip = 1
    agent = Agent(model = model,
                window_size = window_size,
                trend = close,
                skip = skip,
                initial_money = initial_money)
    agent.fit(iterations = iterations, checkpoint = checkpoint)

    # states_buy, states_sell, total_gains, invest = agent.buy()

    return agent

def run_once(company, iterations=500, initial_money=10000):

    model = make_model(company)
    return make_agent(model, initial_money,iterations)


# agent = run_once("AMZN", iterations=500)
# close = agent.trend
# name = "MYfile"
# states_buy, states_sell, total_gains, invest = agent.buy()

# fig = plt.figure(figsize = (15,5))
# plt.plot(close, color='r', lw=2.)
# plt.plot(close, '^', markersize=10, color='m', label = 'buying signal', markevery = states_buy)
# plt.plot(close, 'v', markersize=10, color='k', label = 'selling signal', markevery = states_sell)
# plt.title('total gains %f, total investment %f%%'%(total_gains, invest))
# plt.legend()
# plt.savefig('output/'+name+'.png')
# plt.show()