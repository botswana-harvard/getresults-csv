[![Build Status](https://travis-ci.org/botswana-harvard/getresults-csv.svg?branch=develop)](https://travis-ci.org/botswana-harvard/getresults-csv)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-csv/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/getresults-csv?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/getresults-csv/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/getresults-csv/develop)

# getresults-csv

Import laboratory result from a CSV file.

Add to settings:

	INSTALLED_APPS = (
	    ...
	    'getresults_csv',
	    ...
	)

	CSV_FILE_PATH = '~/interface/cd4/'
	CSV_FILE_EXT = [('*.csv', '*\.csv$'), ]

CSV_FILE_EXT is a tuple of the file pattern and the regex file pattern used by Django FileField.

Create a subbfolder of CSV_FILE_PATH named 'archive'.

Define a csv format. This can be done in admin. 

	from getresults_csv.models import CsvFormat
	
	CsvFormat.objects.create()

Start the observer (overrides settings above):

	python manage.py start_observer multiset ~/interface/cd4
	
The `testdata` folder has sample CSV files to configure csv_format, csv_dictionaries, etc. You could create similar files to meet your needs and then use the util loaders to load the information.  

Defining a SaveHandler

The observer accepts custom SaveHandler classes. There is a BD FACSCalibur Multiset SaveHandler in the `getresults` subfolder of this repo. Use this as an example for customization.
 