class Questionansmappingrequest:
    id = None
    vendor_id = None
    Activity = None
    question_type = None
    period = None
    periodicity = None
    remarks = None
    type_status = None
    period_start = None
    period_end = None

    def __init__(self, resp_obj):

        if 'id' in resp_obj:
            self.id = resp_obj['id']
        if 'vendor_id' in resp_obj:
            self.vendor_id = resp_obj['vendor_id']
        if 'Activity' in resp_obj:
            self.Activity = resp_obj['Activity']
        if 'question_type' in resp_obj:
            self.question_type = resp_obj['question_type']
        if 'period' in resp_obj:
            self.period = resp_obj['period']
        if 'periodicity' in resp_obj:
            self.periodicity = resp_obj['periodicity']
        if 'remarks' in resp_obj:
            self.remarks = resp_obj['remarks']
        if 'type_status' in resp_obj:
            self.type_status = resp_obj['type_status']
        if 'period_start' in resp_obj:
            self.period_start = resp_obj['period_start']
        if 'period_end' in resp_obj:
            self.period_end = resp_obj['period_end']

    def get_id(self):
        return self.id
    def get_vendor_id(self):
        return self.vendor_id
    def get_Activity(self):
        return self.Activity
    def get_question_type(self):
        return self.question_type
    def get_period(self):
        return self.period
    def get_periodicity(self):
        return self.periodicity
    def get_remarks(self):
        return self.remarks
    def get_type_status(self):
        return self.type_status
    def get_period_start(self):
        return self.period_start
    def get_period_end(self):
        return self.period_end
