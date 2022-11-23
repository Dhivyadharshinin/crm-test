import json


class TourApprovedby:
    id = None
    approvedby = None
    onbehalfof = None
    approveddate = None
    apptype = None
    applevel = None
    appcomment = None
    status = None
    tour_id = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


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


class Ecf_req:
    id = None
    # approvedby = None
    # onbehalfof = None
    # approveddate = None
    # apptype = None
    # applevel = None
    # appcomment = None
    # Entity_Gid = None
    tourgid = None
    type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        # if 'approvedby' in tour_obj:
        #     self.approvedby = tour_obj['approvedby']
        # if 'onbehalfof' in tour_obj:
        #     self.onbehalfof = tour_obj['onbehalfof']
        # if 'approveddate' in tour_obj:
        #     self.approveddate = tour_obj['approveddate']
        # if 'apptype' in tour_obj:
        #     self.apptype = tour_obj['apptype']
        # if 'applevel' in tour_obj:
        #     self.applevel = tour_obj['applevel']
        # if 'appcomment' in tour_obj:
        #     self.appcomment = tour_obj['appcomment']
        # if 'Entity_Gid' in tour_obj:
        #     self.Entity_Gid = tour_obj['Entity_Gid']
        if 'tourgid' in tour_obj:
            self.tourgid = tour_obj['tourgid']
        if 'type' in tour_obj:
            self.type = tour_obj['type']

