import json
class TourApprovedbyResponse:
    id = None
    approvedby = None
    onbehalfof = 0
    approveddate = None
    apptype = None
    applevel = 2
    appcomment = None
    status = 4
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