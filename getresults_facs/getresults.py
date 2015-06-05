import csv
import os


class Result:
    def __init__(self, result_as_dict):
        self.as_dict = result_as_dict

    @property
    def panel(self):
        return self.as_dict['Panel Name']

class GetResults:

    def __init__(self, filename, panel, encoding=None):
        self.filename = os.path.expanduser(filename)
        self.encoding = encoding or 'utf-8'  # mac_roman
        self.results = {}
        self.panel = None
        self.empty = '.'

    def load(self):
        with open(self.filename, encoding=self.encoding, newline='') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
            for values in reader:
                result = dict(zip(header, values))
                self.results[result['Sample ID']] = result
                if not self.panel:
                    self.panel = Panel(result['Panel Name'])
                if self.panel != result['Panel Name']:
                    raise ValueError()

    def panel_name(self):
        pass
