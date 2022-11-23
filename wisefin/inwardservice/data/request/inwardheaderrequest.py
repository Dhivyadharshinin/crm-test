import json

class HeaderRequest:
    id = None
    no = None
    date = None
    channel = None
    courier = -1
    awbno = None
    noofpockets = None
    inwardfrom = None
    receivedby = None
    branch = None

    def __init__(self, header_obj):
        if 'id' in header_obj:
            self.id = header_obj['id']
        if 'no' in header_obj:
            self.no = header_obj['no']
        if 'date' in header_obj:
            self.date = header_obj['date']
        if 'noofpockets' in header_obj:
            self.noofpockets = header_obj['noofpockets']
        if 'channel_id' in header_obj:
            self.channel = header_obj['channel_id']
        if 'courier_id' in header_obj:
            self.courier = header_obj['courier_id']
        if 'branch_id' in header_obj:
            self.branch = header_obj['branch_id']
        if 'awbno' in header_obj:
            self.awbno = header_obj['awbno']
        if 'inwardfrom' in header_obj:
            self.inwardfrom = header_obj['inwardfrom']
        # if 'receivedby' in header_obj:
        #     self.receivedby = header_obj['receivedby']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_no(self):
        return self.no

    def get_date(self):
        return self.date
    def get_noofpockets(self):
        return self.noofpockets

    def get_channel(self):
        return self.channel

    def get_courier(self):
        return self.courier

    def get_awbno(self):
        return self.awbno

    def get_inwardfrom(self):
        return self.inwardfrom
    def get_branch(self):
        return self.branch
