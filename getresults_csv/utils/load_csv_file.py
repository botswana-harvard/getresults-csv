import os
import sys

from unipath import Path


def load_csv_file(path, files):
    path = Path(os.path.expanduser(path))
    sys.stdout.write('Importing from {}...\n'.format(str(path)))
    for filename, load_func in files:
        sys.stdout.write('    {}'.format(filename))
        load_func(os.path.join(path, filename))
        sys.stdout.write('. OK\n')
    sys.stdout.write('Done.\n'.format(str(path)))
