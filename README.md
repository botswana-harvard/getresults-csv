[![Build Status](https://travis-ci.org/botswana-harvard/getresults-facs.svg?branch=master)](https://travis-ci.org/botswana-harvard/getresults-facs)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-facs/badge.svg)](https://coveralls.io/r/botswana-harvard/getresults-facs)
[![Documentation Status](https://readthedocs.org/projects/getresults-facs/badge/?version=latest)](https://readthedocs.org/projects/getresults-facs/?badge=latest)
[![PyPI version](https://badge.fury.io/py/getresults-facs.svg)](http://badge.fury.io/py/getresults-facs)
[![Code Health](https://landscape.io/github/botswana-harvard/getresults-facs/master/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/getresults-facs/master)

# getresults-facs

import result files exported from BD FACSCalibur through Multiset.

Usage (so far):

Load panels from a CSV file into model Panel/PanelMapping:

    from getresults_facs.utils import load_panels_from_csv

    # panels define the relevant fields in the file.
    # a panel is made up of items where each item represents a utestid
    # panels are defined in multiset but a sample panel.csv is in this repo.
    # just need to do this once
    
    load_panels_from_csv()
    load_utestids_from_csv()
    load_panel_items_from_csv()
    
Load a Multiset CSV file into models Result/ResultItem:

    from getresults_facs.getresults import GetResults
    
    # a sample file is available as testdata

    filename = '~/source/getresults-facs/getresults_facs/testdata/rad9A6A3.tmp'

    
    # load the file and setup the class
    # encode as 'mac_roman' since Multiset runs on a Mac

    gr = GetResults(filename, encoding='mac_roman')


    # save to the result model 
    # we just want CD4 Abs/%, CD8 Abs/% and some assay details like date and operator

    gr.save()


    # the results should now be validated before release for clinical use.
    
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
