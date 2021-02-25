import numpy as np


class Node:
    def __init__(self, value):
        self.value = value

    def evaluate(self, asset):
        raise NotImplementedError


class Feature(Node):
    def evaluate(self, asset):
        return asset[self.value]


class Constant(Node):
    def evaluate(self, asset):
        return self.value


class Factor:
    def __init__(self, left: Feature, right: Node, comparator):
        self.left = left
        self.right = right
        self.comparator = comparator

    def evaluate(self, asset):
        return self.comparator(self.left.evaluate(asset), self.right.evaluate(asset))


class BuyAndHold(Factor):
    @staticmethod
    def evaluate(asset):
        return np.ones(len(asset['close'])).astype(bool)
