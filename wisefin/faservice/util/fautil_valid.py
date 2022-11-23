from faservice.util.fautil import SourceType
from datetime import datetime

def source_valdaition(source):
    source_array=[SourceType.PO, SourceType.SPLIT,SourceType.MERGE,SourceType.NON_PO]

    if source not in source_array:
        return False
    else:
        return True

def date_validation(from_date,to_date):
    split_from = datetime.strptime(from_date, '%Y-%m-%d').date()
    split_todate = datetime.strptime(to_date, '%Y-%m-%d').date()
    if split_from > split_todate:
        return True
    return False