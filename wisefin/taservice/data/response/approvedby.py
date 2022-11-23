import json


class TourApprovedbyResponse:

    id = None
    approvedby = None
    onbehalfof = None
    approveddate = None
    apptype = None
    applevel = None
    appcomment = None
    status = None
    data=[]


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

    def set_data(self, data):
        self.data = data