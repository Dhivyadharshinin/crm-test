import json
from taservice.util.ta_util import Status,Onbehalfof,App_level,App_type

class TourApprovedbyRequest:
    id = None
    approvedby = None
    onbehalfof = Onbehalfof.ZERO
    approveddate = None
    # apptype = App_type.ADVANCE
    applevel = App_level.THIRD_LEVEL
    appcomment = None
    status = Status.REJECTED
    tour_id = None
    appamount = None
    onbehalf = None
    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'approvedby' in tour_obj:
            self.approvedby = tour_obj['approvedby']
        if 'onbehalfof' in tour_obj:
            self.onbehalfof = tour_obj['onbehalfof']
        if 'approveddate' in tour_obj:
            self.approveddate = tour_obj['approveddate']
        if 'apptype' in tour_obj:
            self.apptype = tour_obj['apptype']
        if 'applevel' in tour_obj:
            self.applevel = tour_obj['applevel']
        if 'appcomment' in tour_obj:
            self.appcomment = tour_obj['appcomment']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'appamount' in tour_obj:
            self.appamount = tour_obj['appamount']
        if 'onbehalf' in tour_obj:
            self.onbehalf = tour_obj['onbehalf']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_approvedby(self, approvedby):
        self.approvedby = approvedby
    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof
    def set_approveddate(self, approveddate):
        self.approveddate = approveddate
    def set_apptype(self, apptype):
        self.apptype = apptype
    def set_applevel(self, applevel):
        self.applevel = applevel
    def set_appcomment(self, appcomment):
        self.appcomment = appcomment
    def set_status(self, status):
        self.status = status
    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def get_id(self):
        return self.id
    def get_approvedby(self):
        return self.approvedby
    def get_onbehalfof(self):
        return self.onbehalfof
    def get_approveddate(self):
        return self.approveddate
    def get_apptype(self):
        return self.apptype
    def get_applevel(self):
        return self.applevel
    def get_appcomment(self):
        return self.appcomment
    def get_status(self):
        return self.status
    def get_tour_id(self):
        return self.tour_id
