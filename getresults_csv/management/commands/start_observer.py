import os
import socket
import sys

from builtins import ConnectionResetError, ConnectionRefusedError
from django.core.management.base import BaseCommand, CommandError
from paramiko import SSHException

from getresults_csv.server import Server
from getresults_csv.csv_file_handler import CsvFileHandler
from getresults_csv.getresults import Multiset2DMISSaveHandler as SaveHandler


class Command(BaseCommand):
    args = '<csv_format_name> <source_dir>'

    def handle(self, *args, **options):
        csv_format = args[0]
        source_dir = args[1]
        archive_dir = os.path.join(source_dir, 'archive')
        save_handler = SaveHandler()
        file_patterns = save_handler.file_patterns
        event_handler = CsvFileHandler(
            csv_format=csv_format,
            source_dir=source_dir,
            archive_dir=archive_dir,
            patterns=file_patterns,
            save_handler=save_handler)
        try:
            server = Server(event_handler)
        except (ConnectionResetError, SSHException, ConnectionRefusedError, socket.gaierror) as e:
            raise CommandError(str(e))
        sys.stdout.write('\n' + str(server) + '\n')
        sys.stdout.write('CSV format: {}\n'.format(server.event_handler.csv_format.name))
        sys.stdout.write('File patterns: {}\n'.format(','.join([x for x in server.event_handler.patterns])))
        sys.stdout.write('Source folder: {}\n'.format(server.event_handler.source_dir))
        sys.stdout.write('Archive folder: {}\n'.format(server.event_handler.archive_dir))
        sys.stdout.write('\npress CTRL-C to stop.\n\n')
        server.observe()
