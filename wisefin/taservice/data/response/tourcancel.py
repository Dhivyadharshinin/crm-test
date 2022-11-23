import json

class TourCancelres:

    id = None
    type = None
    status = 1
    approval = None
    tour_id = None
    onbehalfof = None
    apptype = None
    appcomment = None
    approvedby = None
    applevel = None
    approveddate = None
    data = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type(self, type):
        self.type = type

    def set_status(self, status):
        self.status = status

    def set_data(self, data):
        self.data = data

    def set_approval(self, approval):
        self.approval = approval

    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof

    def set_apptype(self, apptype):
        self.apptype = apptype

    def set_appcomment(self, appcomment):
        self.appcomment = appcomment

    def set_approvedby(self, approvedby):
        self.approvedby = approvedby

    def set_applevel(self, applevel):
        self.applevel = applevel

    def set_approveddate(self, approveddate):
        self.approveddate = approveddate

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

