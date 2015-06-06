[![Build Status](https://travis-ci.org/erikvw/getresults-facs.svg?branch=master)](https://travis-ci.org/erikvw/getresults-facs)
[![Coverage Status](https://coveralls.io/repos/erikvw/getresults-facs/badge.svg)](https://coveralls.io/r/erikvw/getresults-facs)
[![Documentation Status](https://readthedocs.org/projects/getresults-facs/badge/?version=latest)](https://readthedocs.org/projects/getresults-facs/?badge=latest)
[![PyPI version](https://badge.fury.io/py/getresults-facs.svg)](http://badge.fury.io/py/getresults-facs)
[![Code Health](https://landscape.io/github/erikvw/getresults-facs/master/landscape.svg?style=flat)](https://landscape.io/github/erikvw/getresults-facs/master)

# getresults-facs

import result files exported from BD FACSCalibur through Multiset.

Usage (so far):

Load panels from a CSV file into model Panel/PanelMapping:

    from getresults_facs.utils import load_panels_from_csv

    # panels define the relevant fields in the file.
    # panels are defined in multiset.
    # just need to do this once
    load_panels_from_csv()
    
Load a Multiset CSV file into models Result/ResultItem:

    from getresults_facs.classes import Result
    from getresults_facs.getresults import GetResults
    
    # a sample file is available as testdata
    filename = '~/source/getresults-facs/getresults_facs/testdata/rad9A6A3.tmp'
    
    # load the file and setup the class
    # encode as 'mac_roman' since Multiset runs on a Mac
    gr = GetResults(filename, Result, encoding='mac_roman')
    
    # save to the result model 
    # we just want CD4 Abs/%, CD8 Abs/% and some assay details like date and operator
    gr.save()

	# the results should now be validated before release for clinical use.
    
