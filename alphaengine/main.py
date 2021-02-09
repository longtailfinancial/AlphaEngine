import glob
import csv


class Source:
    def __init__(self, directory, file_type='.csv'):
        self.directory = directory
        self.file_type = file_type

        self.glob_string = f'{self.directory}*{self.file_type}'
        self.data = {}

    @property
    def instrument_filenames(self):
        return glob.glob(self.glob_string)

    @property
    def instrument_names(self):
        return [i[len(self.directory):-len(self.file_type)] for i in self.instrument_filenames]

    def format_row(self, *args):
        raise NotImplementedError

    def __getitem__(self, key):
        # Check the cache
        item = self.data.get(key)
        if item is not None:
            return item

        # Optimistically open the file. If it isn't there, the error is informative.
        filename = f'{self.directory}{key}{self.file_type}'
        with open(filename) as f:
            item = []
            reader = csv.reader(f)
            for row in reader:
                _row = self.format_row(row)
                item.append(_row)

        self.data[key] = item

        return item

