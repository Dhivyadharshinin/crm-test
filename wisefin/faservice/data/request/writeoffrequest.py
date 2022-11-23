class WriteOffRequest:
    id = None
    assetdetails_id = None
    date = None
    writeoff_status = None
    reason = None
    value = None

    def __init__(self, data_obj):
        if 'id' in data_obj:
            self.id = data_obj['id']
        if 'assetdetails_id' in data_obj:
            self.assetdetails_id = data_obj['assetdetails_id']
        if 'date' in data_obj:
            self.date = data_obj['date']
        if 'writeoff_status' in data_obj:
            self.writeoff_status = data_obj['writeoff_status']
        if 'reason' in data_obj:
            self.reason = data_obj['reason']
        if 'value' in data_obj:
            self.value = data_obj['value']

    def get_id(self):
        return self.id

    def get_assetdetails_id(self):
        return self.assetdetails_id

    def get_date(self):
        return self.date

    def get_writeoff_status(self):
        return self.writeoff_status

    def get_reason(self):
        return self.reason

    def get_value(self):
        return self.value