# getresults-facs

import result files exported from FACS Multiset

Usage (so far):

Load panels from a CSV file:

    from getresults_facs.utils import load_panels_from_csv
    
    load_panels_from_csv()
    
Load a Multiset CSV file:

    from getresults_facs.classes import Result
    from getresults_facs.getresults import GetResults
    
    filename = '~/source/getresults-facs/getresults_facs/testdata/rad9A6A3.tmp'
    gr = GetResults(filename, Result, encoding='mac_roman')
    gr.save()
