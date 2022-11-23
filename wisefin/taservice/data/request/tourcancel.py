import json

class TourCancelreq:
    id = None
    type = None
    status = 1
    tour_id = None
    approval = None
    onbehalfof = 0
    apptype = None
    appcomment = None
    approvedby = 1
    approveddate = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'type' in tour_obj:
            self.type = tour_obj['type']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'approval' in tour_obj:
            self.approval = tour_obj['approval']
        if 'onbehalfof' in tour_obj:
            self.onbehalfof = tour_obj['onbehalfof']
        if 'apptype' in tour_obj:
            self.apptype = tour_obj['apptype']
        if 'appcomment' in tour_obj:
            self.appcomment = tour_obj['appcomment']
        if 'approvedby' in tour_obj:
            self.approvedby = tour_obj['approvedby']
        if 'approveddate' in tour_obj:
            self.approveddate = tour_obj['approveddate']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_status(self):
        return self.status

    def get_approval(self):
        return self.approval

    def get_tour_id(self):
        return self.tour_id

    def get_onbehalfof(self):
        return self.onbehalfof

    def get_apptype(self):
        return self.apptype

    def get_appcomment(self):
        return self.appcomment

    def get_approvedby(self):
        return self.approvedby

    def get_approveddate(self):
        return self.approveddate


