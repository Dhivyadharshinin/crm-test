import json

class WriteOffResponse:
    id = None
    assetdetails_id = None
    date = None
    writeoff_status = None
    reason = None
    value = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_assetdetails_id(self, assetdetails_id):
        self.assetdetails_id = assetdetails_id
    def set_date(self,date):
        self.date = date
    def set_writeoff_status(self, writeoff_status):
        self.writeoff_status = writeoff_status
    def set_reason(self, reason):
        self.reason = reason
    def set_value(self, value):
        self.value = value
