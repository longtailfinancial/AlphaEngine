import numpy as np
import csv
from datetime import datetime


# The basic CSV instrument. We'll abstract this later when we need it
class FileInstrument:
    def __init__(self, filename, load=True):
        self.datetime_format = '%d-%b-%Y'
        self.column_names = ['day', 'month', 'year', 'open', 'high', 'low', 'close', 'volume', 'forward_returns']
        self.column_set = set(self.column_names)

        self.data = None

        if load:
            self.load_file(filename)

    def load_file(self, filename):
        with open(filename) as f:
            item = []
            reader = csv.reader(f)
            for row in reader:
                _row = self.format_row(*row)
                item.append(_row)

        item = np.array(item)
        returns = np.expand_dims(np.diff(item[:, -2], append=item[:, -2][-1]), axis=1)

        items_with_returns = np.hstack((item, returns))
        self.data = items_with_returns

    def format_row(self, *args):
        date = datetime.strptime(args[0], self.datetime_format)
        o = float(args[1])
        h = float(args[2])
        l = float(args[3])
        c = float(args[4])
        v = int(args[5])

        return [date.day, date.month, date.year, o, h, l, c, v]

    def attach_feature(self, feature, name):
        self.column_set.add(name)  # this will fail if the feature already exists
        self.column_names.append(name)

        f = np.expand_dims(feature, axis=1)
        self.data = np.hstack((self.data, f))

    def __getitem__(self, key):
        if type(key) == str:
            idx = self.column_names.index(key)
            return self.data[:, idx]

        return self.data.__getitem__(key)

    def __repr__(self):
        return self.data.__repr__()