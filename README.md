[![Build Status](https://travis-ci.org/botswana-harvard/getresults-csv.svg?branch=develop)](https://travis-ci.org/botswana-harvard/getresults-csv)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-csv/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/getresults-csv?branch=develop)
[![Documentation Status](https://readthedocs.org/projects/getresults-csv/badge/?version=latest)](https://readthedocs.org/projects/getresults-csv/?badge=latest)
[![PyPI version](https://badge.fury.io/py/getresults-csv.svg)](http://badge.fury.io/py/getresults-csv)
[![Code Health](https://landscape.io/github/botswana-harvard/getresults-csv/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/getresults-csv/develop)

# getresults-csv

import CSV result files.

By default can import BD FACSCalibur Multiset export file.

Usage:
======

Management Commands
-------------------

Load definitions (see testdata folder for examples):

	python manage.py import_definitions <path>

Import a Multiset result file

    python manage.py import_result_file 15052015.csv

Import a result file names 'vl.csv' with a pre-defined CSV header 'amplicore' delimiter by a comma:

    python manage.py import_result_file vl.csv --csv_header_name=amplicore --delimiter=,


Manually in manage.py shell
------------------

Load definitions.

    from getresults_csv.utils import *

    load_panels_from_csv()
    load_utestids_from_csv()
    load_panel_items_from_csv()
    load_csv_headers_from_csv()
    
Load a Multiset CSV file into models Result/ResultItem:

    import os
    from unipath import Path
    from getresults_csv.getresults import GetResults
    
    # a sample file is available as testdata

    filename = Path(os.path.expanduser('~/source/getresults-csv/getresults_csv/testdata/rad9A6A3.tmp'))

    # load the file and setup the class
    # encode as 'mac_roman' since Multiset runs on a Mac

    gr = GetResults(filename, encoding='mac_roman')

    # save to the result model 
    # we just want CD4 Abs/%, CD8 Abs/% and some assay details like date and operator

    gr.save()

    # the results should now be validated before release for clinical use.

See what was imported:
	
	from getresults_csv.models import Result, ResultItem
	
	Result.objects.all()
	[<Result: AA11562: cd3/cd8/cd45/cd4 truc>, <Result: AA11528: cd3/cd8/cd45/cd4 truc>, ...]
	ResultItem.objects.all()
	[<ResultItem: cd4: AA11562: cd3/cd8/cd45/cd4 truc>, <ResultItem: cd4%: AA11562: cd3/cd8/cd45/cd4 truc>, ...]


Definitions
===========

The testdata/ folder has sample files of each of these.

Panels
------
A panel is a named group of items where each item represents a result. For example, a CD4 panel might
consist of CD4 Absolute, CD4%, CD8 Absolute and CD8%. A clinic orders a CD4 but expects 4 values on the report.

Panel Items
-----------
A panel item represents one item in the panel. It is the link between a the panel and a Utestid.

Utestids
--------
A Utestid (Universal Test Identifier) represents one result item in a panel. It has attributes and methods
that further define the result value. For example, the test may be limited to lower and upper limits of
detection where a raw value, say 300, if below the lower limit of detection, say 400, should be reported
as < 400 and not 300.

Utestids can also be calculated. A calculated value is not reported from the analyzer but should be 
included in the result report. For example, an analyzer reports the viral load (PHM) as copies/ml but the report 
requires both the absolute value and the LOG of the value. The LOG is a calculated Utestid (e.g. PHMLOG10).
 
A Utestid may appear in more than one panel.

CSV Headers
-----------
Link a header row with handled fields in GetResults for a file type, e.g. Multiset.
 
