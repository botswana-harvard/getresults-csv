

class Multiset2DMISSaveHandler(object):
    """Save multiset CSV data to DMIS."""

    def save(self, csv_format, csv_results):
        # look up received sample ?
        # update l5
        for result_identifier, csv_result_item in csv_results.items():
            print(csv_result_item.as_dict())
            break
