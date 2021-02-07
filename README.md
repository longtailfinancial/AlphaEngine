# AlphaEngine
A system to data mine alpha and make money.

## Basic Intro

When you have a trading idea, it's usually something you can write in words such as: "If I take out a trade when X happens, will I make money?" There is not a good backtester or computer program to then take this, digitize it, and answer your question in a consise way. That's what the Alpha Engine is for. The goal is to take a question about a trading signal and return a decent answer which allows you to decide whether or not it is in fact a useful signal.

From there, the Alpha Engine can be automated by things like genetic algorithms that come up with the questions automatically and systems that filter only certain results based on the metrics that come out of it.

The goals of the project are:
1. Simplicity
2. Extendability
3. Speed

Therefore, the core focus of the engine itself is purely on the question / answer loop. Once we achieve the 3 goals of the project, we can move onto the 'fun' stuff like extending the search space, etc.

## High Level Idea
The idea is to take raw price data, put it into a numpy array, and calculate the t+1 turns. This is the main data that we work with.

From there, we can calculate transforms and additional signals like EMA, etc.

In the end, we come up with a Numpy boolean array that structures our question. For example, if we want to test if buying on a certain day every year is profitable, we create a Numpy boolean filter with some logic and select the rows that fulfill that requirement. From there, we know the immediate t+1 returns.

These become our 'entry' rows. We then can have some basic rules for 'exits.' Let's assume it's just time based for simplicity now (5 days or so). This is easy because then we can just roll the returns forward t+5 time steps and do a cumulative sum to get the total returns for the time period.

This method makes it extremely fast and vectorizable to search and calculate massive amounts of data.

For example, the shape of a single stock of daily returns over 20 years is ~(5000, 8). This assumes the features of year, month, day, open, high, low, close, and forward returns.

Across the stock universe, there is probably about 6000 stocks on the NASDAQ and NYSE. This creates a Numpy array of (6000, 5000, 8). This, in machine learning and data mining terms, is a very small matrix.

## The Loop

### Raw Data
Raw data is what you derive all of your signals from. This means the Open, High, Low, Close, Volume, bars, the tick bars, the order book data, or whatever you are using. However, this is the *base*. This does not include any transformations of this data that you then use to ask questions.

For example, the EMA of the raw data is *not* the raw data! This is a transformation of the raw data, so it happens later. The EMA is a feature of the raw data.

Raw data can be stored anywhere.
