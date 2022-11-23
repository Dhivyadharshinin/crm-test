import json

from masterservice.util.masterutil import Vendorclassfication_type
from vendorservice.util.vendorutil import get_period, get_periodicity, get_type_status


class Questionansmappingresponse:
    id = None
    vendor = None
    Activity = None
    question_type = None
    period = None
    periodicity = None
    remarks = None
    type_status = None
    period_start = None
    period_end = None
    expiry = True

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_vendor(self, vendor):
        self.vendor = vendor
    def set_Activity(self, Activity):
        self.Activity = Activity
    def set_question_type(self, question_type):
        self.question_type = question_type
    def set_period(self, period):
        self.period = Vendorclassfication_type(period)
    def set_periodicity(self, periodicity):
        self.periodicity = get_periodicity(periodicity)
    def set_remarks(self, remarks):
        self.remarks = remarks
    def set_type_status(self, type_status):
        self.type_status = get_type_status(type_status)
    def set_mapping(self, mapping):
        self.mapping = mapping

    def set_period_start(self, period_start):
        self.period_start = str(period_start)

    def set_period_end(self, period_end):
        self.period_end = str(period_end)

    def set_expiry(self, expiry):
        self.expiry = expiry
