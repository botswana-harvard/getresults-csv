

class CsvResultRecordItem(object):
    """Represents a single result item within a result.

    For example CD4 Abs within a CD4 Panel of CD4 Abs, CD4%, CD8 Abs, CD8%.
    """
    def __init__(self, panel_item, utestid, value, result_datetime, status, sender, operator):
        self.panel_item = panel_item
        self.reportable_value = utestid.value_with_quantifier(value)
        self.value = value
        self.result_datetime = result_datetime
        self.completed_at = result_datetime
        self.sender = sender
        self.status = status
        self.utestid = utestid
        self.operator = operator

    def __repr__(self):
        return '{}({},{}...)'.format(self.__class__.__name__, self.panel_item, self.utestid)

    def __str__(self):
        return '{}: {}'.format(self.utestid, ' '.join(self.reportable_value))
