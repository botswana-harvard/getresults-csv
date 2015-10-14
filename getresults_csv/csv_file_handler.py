from fnmatch import filter
from datetime import datetime
from django.utils import timezone
from os.path import join
from os import listdir
from shutil import move
from watchdog.events import PatternMatchingEventHandler

from getresults_csv.models import CsvFormat

from .csv_result import CsvResult


class CsvFileHandler(PatternMatchingEventHandler):

    def __init__(self, csv_format, source_dir, archive_dir, patterns=None, save_handler=None):
        self.csv_format = CsvFormat.objects.get(name=csv_format)
        self.source_dir = source_dir
        self.archive_dir = archive_dir
        self.save_handler = save_handler
        super(CsvFileHandler, self).__init__(patterns=patterns, ignore_directories=True)

    def connect(self):
        pass

    def process_existing_files(self):
        """Process existing files on startup."""
        print('{} {}.'.format(timezone.now(), 'processing existing files on start...'))
        for src_path in self.matching_files:
            self.process(type('event', (object, ), {'event_type': 'exists', 'src_path': src_path})())
        print('{} done processing existing files.'.format(timezone.now()))
        print('{} waiting ...'.format(timezone.now()))

    def process(self, event):
        """Process files on a file event."""
        try:
            path = event.dest_path
        except AttributeError:
            path = event.src_path
        print('{} {} \'{}\'.'.format(
            timezone.now(), event.event_type, self.get_filename(path)))
        self.read_csv_files(path)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        print('{} {} file \'{}\' from source folder.'.format(
            timezone.now(), event.event_type, self.get_filename(event.src_path)))

    def on_moved(self, event):
        self.process(event)

    def read_csv_files(self, src_path):
        try:
            csv_result = CsvResult(self.csv_format, src_path, save_handler=self.save_handler)
            print('{} loaded file\'{}\' using CSV format \'{}\'.'.format(
                timezone.now(), self.get_filename(src_path), self.csv_format.name))
            csv_result.save()
            print('{} saved data for file \'{}\'.'.format(
                timezone.now(), self.get_filename(src_path)))
            self.move_to_archive(src_path)
        except ValueError:
            print('{} failed to load \'{}\' using CSV format \'{}\'. Invalid format'.format(
                timezone.now(), self.get_filename(src_path), self.csv_format.name))

    def move_to_archive(self, src_path):
        filename = self.get_filename(src_path)
        timestamp = datetime.now().strftime('%Y%m%d%H%m%s')
        src = join(self.source_dir, filename)
        dst = join(self.archive_dir, '{}.{}'.format(filename, timestamp))
        move(src, dst)
        print('{} moved file \'{}\' to archive'.format(timezone.now(), filename))

    def get_filename(self, path):
        return path.split(self.source_dir)[1].replace('/', '')

    @property
    def matching_files(self):
        for file_pattern in self.patterns:
            for file in filter(listdir(self.source_dir), file_pattern):
                yield join(self.source_dir, file)
