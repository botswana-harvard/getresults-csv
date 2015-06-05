[![Build Status](https://travis-ci.org/erikvw/getresults-facs.svg?branch=master)](https://travis-ci.org/erikvw/getresults-facs)
[![Coverage Status](https://coveralls.io/repos/erikvw/getresults-facs/badge.svg)](https://coveralls.io/r/erikvw/getresults-facs)
[![Documentation Status](https://readthedocs.org/projects/getresults-facs/badge/?version=latest)](https://readthedocs.org/projects/getresults-facs/?badge=latest)
[![PyPI version](https://badge.fury.io/py/getresults-facs.svg)](http://badge.fury.io/py/getresults-facs)
[![Code Health](https://landscape.io/github/erikvw/getresults-facs/master/landscape.svg?style=flat)](https://landscape.io/github/erikvw/getresults-facs/master)

# getresults-facs

import result files exported from FACS Multiset

Usage (so far):

Load panels from a CSV file into model Panel/PanelMapping:

    from getresults_facs.utils import load_panels_from_csv
    
    load_panels_from_csv()
    
Load a Multiset CSV file into models Result/ResultItem:

    from getresults_facs.classes import Result
    from getresults_facs.getresults import GetResults
    
    filename = '~/source/getresults-facs/getresults_facs/testdata/rad9A6A3.tmp'
    gr = GetResults(filename, Result, encoding='mac_roman')
    gr.save()
