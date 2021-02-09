import csv
import glob
from datetime import datetime
import os


class PriceLoader:
    def __init__(self):
        self.directory = os.path.dirname(__file__) + '/prices/{}/{}.csv'
        self.exchanges = ['NASDAQ', 'AMEX', 'FOREX', 'NYSE', 'OTCBB']
        self.glob = 'prices/{}/*.csv'

    def format_row(self, row):
        d, o, h, l, c, v = row
        date = datetime.strptime(d, '%d-%b-%Y')
        return date, float(o), float(h), float(l), float(c), int(v)

    def load(self, exchange, symbol):
        file = self.directory.format(exchange, symbol)

        prices = []
        with open(file) as f:
            reader = csv.reader(f)
            for row in reader:
                prices.append(self.format_row(row))

        return prices

    def symbols(self, exchange):
        files = glob.glob(self.glob.format(exchange))

        symbols = []
        for file in files:
            file = file.replace('prices/{}/'.format(exchange), '')
            file = file.replace('.csv', '')
            symbols.append(file)

        symbols.sort()
        return symbols
