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

    def load_source(self, location):
        raise NotImplementedError

    def __getitem__(self, key):
        # Check the cache
        item = self.data.get(key)
        if item is not None:
            return item

        # Optimistically open the file. If it isn't there, the error is informative.
        filename = f'{self.directory}{key}{self.file_type}'

        item = self.load_source(filename)
        self.data[key] = item

        return item


class EODDataSource(Source):
    def __init__(self, *args, **kwargs):
        self.datetime_format = '%d-%b-%Y'
        super().__init__(*args, **kwargs)

    def load_source(self, location):
        with open(location) as f:
            item = []
            reader = csv.reader(f)
            for row in reader:
                _row = self.format_row(*row)
                item.append(_row)

        item = np.array(item)
        returns = np.expand_dims(np.diff(item[:, -2], prepend=0), axis=1)

        items_with_returns = np.hstack((item, returns))

        return items_with_returns

    def format_row(self, *args):
        date = datetime.strptime(args[0], self.datetime_format)
        o = float(args[1])
        h = float(args[2])
        l = float(args[3])
        c = float(args[4])
        v = int(args[5])

        return [date.day, date.month, date.year, o, h, l, c, v]
