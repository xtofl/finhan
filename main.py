from pathlib import Path
from argparse import ArgumentParser
import numpy as np
from matplotlib import pyplot
from pandas import read_csv


def bepost_format_choose(line, dirty, clean):
    if 'ancontact' in line:
        return dirty

    return clean


def transactions(path: Path):
    cleaned, dirty = clean_data(path)

    ts = read_csv(cleaned,
                  delimiter=';', decimal=',',
                  header=1,
                  parse_dates=['Transactie datum', 'Valuta datum'],
                  #day_first=True,
                  engine='python' # cf. https://github.com/pandas-dev/pandas/issues/33699#event-4105125638
                  )
    return ts['Transactie datum', 'Bedrag van de verrichting']

def clean_data(path):
    cleaned, dirties = map(Path, ('clean.prep', 'dirty.prep'))
    with path.open('r') as p, cleaned.open('w') as c, dirties.open('w') as d:
        for i, line in enumerate(p.readlines()):
            target = bepost_format_choose(line, d, c)
            if target is d:
                target.write(f'line {i}: {line}')
            else:
                target.write(line)
    return cleaned, dirties


def plot(what):
    return pyplot.plot_date(what, what)


def main():
    parser = ArgumentParser()
    parser.add_argument('data_path', type=str)
    options = parser.parse_args()
    plot(transactions(Path(options.data_path)))
    pyplot.show()


main()
